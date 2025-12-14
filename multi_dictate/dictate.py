#!/usr/bin/env python3
"""
Fedora Linux Text Dictation Application

Activates with hotkey, records audio, converts to text using Google Speech
Recognition, and pastes the result into the current input field.

interfaces:
    pasimple.PaSimple pulse audio
    webrtcvad.Vad
    speech_recognition.recognize_google
    pyautogui.typewrite
    tkinter.Label

"""

import argparse
import errno
import json
import logging
import os
import difflib
import re
import select
import signal
import subprocess
import sys
import threading
import time
import tkinter as tk
import traceback
import warnings
from io import BytesIO

import pasimple

try:
    subprocess.run(['xhost', '+local:'], capture_output=True, check=False)
except Exception:
    pass

try:
    import pyautogui
except Exception as e:
    logging.getLogger(__name__).warning(f"PyAutoGUI unavailable ({e}); using no-op fallback.")
    import types
    pyautogui = types.SimpleNamespace(
        typewrite=lambda *args, **kwargs: None,
        hotkey=lambda *args, **kwargs: None,
        press=lambda *args, **kwargs: None,
    )
    sys.modules['pyautogui'] = pyautogui
import speech_recognition as sr

warnings.filterwarnings("ignore", category=UserWarning, module="webrtcvad")
import webrtcvad
import yaml
from box import Box
from gtts import gTTS
from pydub import AudioSegment

try:
    from vosk import SetLogLevel
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

try:
    # When running as part of package
    from .kbd_utils import (check_dictation_keybindings, for_typewrite,
                            get_current_keyboard_layout, kbd_cfg)
    from .gemini_processor import GeminiProcessor
    from .openai_processor import OpenAIProcessor
    from .smart_ai_router import SmartAIRouter
    from .qwen_processor import QwenProcessor
except ImportError:
    # When running directly
    from kbd_utils import (check_dictation_keybindings, for_typewrite,
                           get_current_keyboard_layout, kbd_cfg)
    from gemini_processor import GeminiProcessor
    from openai_processor import OpenAIProcessor
    from smart_ai_router import SmartAIRouter
    from qwen_processor import QwenProcessor
# Fix import path for RAG processor
import importlib.util
import os

# Load RAG processor dynamically
rag_path = os.path.join(os.path.dirname(__file__), "simple_rag_processor.py")
spec = importlib.util.spec_from_file_location("simple_rag_processor", rag_path)
simple_rag_module = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(simple_rag_module)
    SimpleRAGProcessor = simple_rag_module.SimpleRAGProcessor
    # RAG loaded successfully
except Exception as e:
    SimpleRAGProcessor = None
    # Failed to load RAG processor - will continue without RAG

# Load optimization processor dynamically
optimization_path = os.path.join(os.path.dirname(__file__), "optimization_processor.py")
spec_opt = importlib.util.spec_from_file_location("optimization_processor", optimization_path)
optimization_module = importlib.util.module_from_spec(spec_opt)
try:
    spec_opt.loader.exec_module(optimization_module)
    OptimizationProcessor = optimization_module.OptimizationProcessor
    # Optimization processor loaded successfully
except Exception as e:
    OptimizationProcessor = None
    # Failed to load optimization processor - will continue without it

# Load prompt engineering optimizer dynamically
prompt_engineering_path = os.path.join(os.path.dirname(__file__), "prompt_engineering_optimizer.py")
spec_pe = importlib.util.spec_from_file_location("prompt_engineering_optimizer", prompt_engineering_path)
prompt_engineering_module = importlib.util.module_from_spec(spec_pe)
try:
    spec_pe.loader.exec_module(prompt_engineering_module)
    PromptEngineeringOptimizer = prompt_engineering_module.PromptEngineeringOptimizer
    # Prompt engineering optimizer loaded successfully
except Exception as e:
    PromptEngineeringOptimizer = None
    # Failed to load prompt engineering optimizer - will continue without it

# Load enhanced reference system dynamically
enhanced_ref_path = os.path.join(os.path.dirname(__file__), "enhanced_reference_system.py")
spec_ref = importlib.util.spec_from_file_location("enhanced_reference_system", enhanced_ref_path)
enhanced_ref_module = importlib.util.module_from_spec(spec_ref)
try:
    spec_ref.loader.exec_module(enhanced_ref_module)
    EnhancedReferenceSystem = enhanced_ref_module.EnhancedReferenceSystem
    # Enhanced reference system loaded successfully
except Exception as e:
    EnhancedReferenceSystem = None
    # Failed to load enhanced reference system - will continue without it

# Only set log level if vosk is available
if VOSK_AVAILABLE:
    SetLogLevel(-1)

FORMAT = pasimple.PA_SAMPLE_S16LE
SAMPLE_WIDTH = pasimple.format2width(FORMAT)
CHANNELS = 1
SAMPLE_RATE = 16000
BYTES_PER_SEC = CHANNELS * SAMPLE_RATE * SAMPLE_WIDTH

params = None
logger = logging.getLogger(os.path.basename(__file__))


class DictationApp:
    """Main dictation application that handles audio recording and speech recognition."""

    def __init__(self):
        y = {}
        # Look for config file in multiple locations
        config_paths = [
            "dictate.yaml",  # Current directory
            os.path.expanduser("~/.config/multi-dictate/dictate.yaml"),  # User config
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "dictate.yaml"),  # Package dir
        ]

        for config_path in config_paths:
            if os.path.exists(config_path):
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        y = yaml.safe_load(f) or {}
                        logger.info(f"Loaded config from {config_path}")
                        break
                except Exception:
                    logger.debug(traceback.format_exc())

        if not y:
            logger.warning("No config file found, using defaults")

        self.cfg = Box(y, default_box=True)
        logger.debug(f"Config general section: {dict(self.cfg.general)}")
        check_dictation_keybindings(self.cfg.keybindings)
        self.recognizer_engine = self.cfg.general.recognizer_engine or "google"
        self.status_window = None
        self.recognizer = sr.Recognizer()
        self.vad = webrtcvad.Vad()
        self.curr_layout = None
        self.cur_lang = None
        self.vad.set_mode(self.cfg.vad.aggressiveness or 0)
        vars(self.recognizer).update(self.cfg.Recognizer)
        self._color_style = "light"
        self._fg_color = None

        self.recognizer_engines = {
            "google": {
                "recognize": self.recognizer.recognize_google,
                "parser": lambda result: result,
            },
        }

        # Only add vosk if available
        if VOSK_AVAILABLE:
            self.recognizer_engines["vosk"] = {
                "recognize": self.recognizer.recognize_vosk,
                "parser": lambda result: json.loads(result).get("text", ""),
            }

        self.gui_queue = []
        self.command = None
        self.recording_active = False
        self.stop_recording_flag = False
        self.continuous_mode_active = False
        self.shutdown_flag = False
        self._cleaned_up = False

        self.commands = {
            "record": (self.start_manual_recording, "Start manual recording till stop"),
            "stop": (self.stop_manual_recording, "Stop manual recording"),
            "toggle": (self._toggle_recording, "Toggle manual recording"),
            "record till pause": (
                self.start_continuous_recording,
                "Start continuous recording till audio pause",
            ),
            "echo": (self._toggle_speech_echo, "Toggle speech echo on/off"),
            "ai_record": (self.start_ai_enhanced_recording, "AI recording with clipboard"),
            "ai_record_shift": (lambda: self.start_ai_enhanced_recording(use_shift_enter=True), "AI recording with clipboard (shift+enter)"),
            "ai_record_clean": (self.start_ai_clean_recording, "AI recording without clipboard"),
            "ai_record_clean_shift": (lambda: self.start_ai_clean_recording(use_shift_enter=True), "AI recording without clipboard (shift+enter)"),
            "clipboard_optimize": (self.optimize_clipboard_prompt, "Optimize clipboard text and copy result"),
        }

        self.tts_lock = threading.Lock()

        # Initialize Smart AI Router (auto-detects and remembers working API)
        ai_provider = self.cfg.general.get('ai_provider', 'auto').lower()

        if ai_provider == 'auto' or ai_provider == 'smart':
            # Use Smart Router - automatically finds and remembers working API
            self.ai_processor = SmartAIRouter(self.cfg)
            logger.info("🧠 Using Smart AI Router (auto-detects best API)")
        elif ai_provider == 'openai':
            # Force OpenAI only
            openai_key = self.cfg.general.get('openai_api_key')
            if openai_key:
                openai_model = self.cfg.general.get('openai_model', 'gpt-4o-mini')
                self.ai_processor = OpenAIProcessor(openai_key, openai_model)
                logger.info(f"✅ Using OpenAI processor with {openai_model}")
            else:
                logger.warning("⚠️  OpenAI selected but no API key configured")
                self.ai_processor = None
        elif ai_provider == 'gemini':
            # Force Gemini only
            if hasattr(self.cfg.general, 'gemini_api_keys'):
                gemini_api_keys = self.cfg.general.gemini_api_keys
            elif hasattr(self.cfg.general, 'gemini_api_key'):
                gemini_api_keys = [self.cfg.general.gemini_api_key]
            else:
                gemini_api_keys = None

            if gemini_api_keys:
                gemini_model = self.cfg.general.gemini_model or "flash"
                self.ai_processor = GeminiProcessor(gemini_api_keys, gemini_model)
                logger.info(f"✅ Using Gemini processor with {gemini_model}")
            else:
                logger.warning("⚠️  Gemini selected but no API keys configured")
                self.ai_processor = None
        elif ai_provider == 'qwen':
            # Force Qwen only
            qwen_model = self.cfg.general.get('qwen_model', 'qwen-turbo')
            try:
                self.ai_processor = QwenProcessor(qwen_model)
                if self.ai_processor.available:
                    logger.info(f"✅ Using Qwen processor with {qwen_model}")
                else:
                    logger.warning("⚠️  Qwen selected but not available (Ollama not running)")
                    self.ai_processor = None
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize Qwen processor: {e}")
                self.ai_processor = None
        else:
            # No AI processing
            self.ai_processor = None
            logger.info("ℹ️  AI processing disabled")

        # Keep backward compatibility
        self.gemini_processor = self.ai_processor

        # Initialize RAG processor (only if enabled)
        rag_config = self.cfg.rag if hasattr(self.cfg, 'rag') else {}
        rag_enabled = rag_config.get('enabled', False)

        if rag_enabled and SimpleRAGProcessor:
            try:
                self.rag_processor = SimpleRAGProcessor(self.cfg)
                logger.info("✅ Simple RAG processor initialized")
            except Exception as e:
                logger.warning(f"⚠️  RAG initialization failed: {e}")
                self.rag_processor = None
        else:
            self.rag_processor = None

        # Initialize PromptEngineeringOptimizer
        if PromptEngineeringOptimizer:
            try:
                self.prompt_optimizer = PromptEngineeringOptimizer(self.cfg)
                logger.info("✅ Prompt Engineering Optimizer initialized")
            except Exception as e:
                logger.warning(f"⚠️  Prompt Optimizer initialization failed: {e}")
                self.prompt_optimizer = None
        else:
            self.prompt_optimizer = None

        # Simplified system - no complex pipelines
        self.rag_processor = None
        logger.info("✅ Simplified AI processing enabled (no 9-stage pipeline)")

    def color_style(self):
        """Detect system color style."""

        self._color_style = "light"
        try:
            r = subprocess.run(
                ['gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'],
                capture_output=True, text=True
            )
            if r.returncode == 0 and 'dark' in r.stdout.lower():
                self._color_style = "dark"
        except Exception:
            pass

        if self._color_style == "light":
            try:
                r = subprocess.run(
                    ['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'],
                    capture_output=True, text=True
                )
                if r.returncode == 0 and 'dark' in r.stdout.lower():
                    self._color_style = "dark"
            except Exception:
                pass

        self._fg_color = self.cfg.colors[self._color_style].fg or 'black'
        logger.debug(self._color_style)
        return self._color_style

    def calibrate(self):
        try:
            import Levenshtein
            distance_fn = Levenshtein.distance
        except ImportError:
            logger.warning("Levenshtein not available, using fallback distance metric")
            import difflib

            def distance_fn(a, b):
                ratio = difflib.SequenceMatcher(None, a, b).ratio()
                return int((1 - ratio) * max(len(a), len(b)))

        """Calibrate voice recognition with all available engines."""
        duration = self.cfg.calibrate.duration or 20
        intro = f"Say this text for calibration of voice recognition during {duration} seconds:"
        orig = (
            self.cfg.calibrate.asr_calibration_text
            or "This quick voice checks sharp sounds, tests warm tone, and sings with vision."
        )
        print("Calibration")
        print(f" {intro}\n\n\u001b[1m{orig}\u001b[0m")
        self.speak_text(intro + orig, sync=True)

        print("Listening 🎤")
        audio = self._convert_raw_audio_to_sr_format(self.record_audio(duration))
        self.speak_text("Thank you.")

        results = []
        print("Recognizing")
        for engine_name, engine_details in self.recognizer_engines.items():
            print(f"  {engine_name}")
            try:
                config = dict(self.cfg[f"recognize_{engine_name}"] or {})
                user = engine_details["parser"](engine_details["recognize"](audio, **config))
                dist = distance_fn(re.sub(r"[^\w\s]", "", orig).lower(), user)
                results.append({"engine": engine_name, "text": user, "dist": dist})
                print(f"    Recognized: '{user}'")
                print(f"    Distance: {dist} (lower is better)")
            except Exception as e:
                print(f"    Error: {e}")
                results.append({"engine": engine_name, "text": "Error", "dist": float("inf")})

        results.sort(key=lambda x: x["dist"])

        if results and results[0]["dist"] < 100:
            print(f"Recommended: {results[0]['engine']}")
        else:
            print("\nCould not determine the best engine.")

    def signal_handler(self, sig, frame):  # pylint: disable=unused-argument
        """Handle SIGINT gracefully."""
        print("\nCaught Ctrl+C, shutting down...")
        self.shutdown_flag = True

    def setup_pasimple_recording(self):
        """Create and return a new pasimple audio recording stream"""
        return pasimple.PaSimple(
            pasimple.PA_STREAM_RECORD,
            FORMAT,
            CHANNELS,
            SAMPLE_RATE,
            app_name="dictate-app",
            stream_name="record-mono",
            maxlength=BYTES_PER_SEC * 2,
            fragsize=BYTES_PER_SEC // 5,
        )

    def _speak_with_gtts(self, text):
        """Try to speak text using gTTS and pasimple."""
        try:
            gtts_config = (self.cfg.gTTS or {}).copy()
            if gtts_config.get("lang", "auto").lower() == "auto":
                gtts_config["lang"] = (
                    kbd_cfg.layouts[self.curr_layout].tts or self.curr_layout
                )
                logger.debug(f"Using TTS language: {gtts_config['lang']}")

            logger.debug(gtts_config)
            tts = gTTS(text, **gtts_config)
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)

            audio = AudioSegment.from_mp3(audio_buffer)
            audio -= 20  # Reduce volume by 20 dB

            logger.debug(
                f"Decoded audio: {audio.channels} channels, "
                f"{audio.frame_rate} Hz, {len(audio.raw_data)} bytes"
            )

            with pasimple.PaSimple(
                pasimple.PA_STREAM_PLAYBACK,
                pasimple.PA_SAMPLE_S16LE,
                audio.channels,
                audio.frame_rate,
                app_name="dictate-app",
                stream_name="playback",
            ) as pa:
                pa.write(audio.raw_data)
                pa.drain()
            return True
        except Exception as e:
            print(f"TTS with gTTS/pasimple failed: {e}")
            logger.debug(traceback.format_exc())
            return False

    def _speak_with_espeak(self, text):
        """Try to speak text using espeak."""
        try:
            subprocess.run(["espeak", "-a", "10", text], check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _speak_with_spd_say(self, text):
        """Try to speak text using spd-say."""
        try:
            subprocess.run(["spd-say", text], check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def speak_text(self, text, sync=False):
        """Convert text to speech using gTTS and pasimple."""
        logger.debug(f"'{text}'")
        if not text:
            return

        def speak_in_thread():
            with self.tts_lock:
                if self._speak_with_gtts(text):
                    return
                if self._speak_with_espeak(text):
                    return
                if self._speak_with_spd_say(text):
                    return
                print(f"All TTS methods failed for: {text}")

        if sync:
            speak_in_thread()
        else:
            threading.Thread(target=speak_in_thread, daemon=True).start()

    def _show_ready_notification(self, text: str):
        """Show notification when text is ready to paste"""
        try:
            # Try using notify-send if available
            subprocess.run([
                'notify-send',
                '-t', '3000',  # 3 seconds
                '-i', 'dialog-information',
                'Multi-Dictate Ready',
                f'✅ Prompt copied to clipboard!\n\n{text[:100]}{"..." if len(text) > 100 else ""}'
            ], check=False, capture_output=True)
        except Exception as e:
            logger.debug(f"Notification failed: {e}")
            # Fallback: just print to console
            print("\n" + "="*50)
            print("✅ PROMPT READY TO PASTE (Ctrl+V)")
            print("="*50)
            print(text)
            print("="*50 + "\n")

    def record_audio(self, max_duration=60, stop_on_silence=False):
        """Record audio manually until stop command or timeout"""
        self.stop_recording_flag = False

        self.curr_layout = get_current_keyboard_layout()
        self.cur_lang = (self.cfg[f"recognize_{self.recognizer_engine}"].language or "auto").lower()
        if self.cur_lang == "auto":
            self.cur_lang = (
                kbd_cfg.layouts[self.curr_layout].stt
                or f"{self.curr_layout}-{self.curr_layout.upper()}"
            )

        # see _recognize
        if (self.cfg.recognize_google.language or "auto").lower() == "auto":
            lc = self.cur_lang.split("-")[0].upper()
            lc2 = f"{lc} " if lc != "EN" else ""
        else:
            lc2 = ""

        self.color_style()
        self.show_status_window(f"Listening {lc2}🎤", "listening")

        pasimple_stream = self.setup_pasimple_recording()
        try:
            return self._record_chunks(pasimple_stream, max_duration, stop_on_silence)
        finally:
            try:
                pasimple_stream.close()
            except Exception:
                pass
            self.hide_status_window()

    def _record_chunks(self, pasimple_stream, max_duration, stop_on_silence=False):
        """Record audio chunks using VAD"""
        logger.debug("")
        chunk_duration_ms = 30
        vad_chunk_size = int(SAMPLE_RATE * (chunk_duration_ms / 1000.0) * SAMPLE_WIDTH)

        pause_threshold_ms = (self.cfg.vad.pause_threshold or 2.0) * 1000
        initial_silence_grace_ms = (self.cfg.vad.initial_silence_grace or 2.0) * 1000
        recorded_audio_chunks = []
        silence = 0
        speech_started = False

        for chunk_num in range(int(max_duration * 1000 / chunk_duration_ms)):
            if self.stop_recording_flag or self.shutdown_flag:
                break

            chunk = pasimple_stream.read(vad_chunk_size)

            recorded_audio_chunks.append(chunk)
            elapsed_ms = chunk_num * chunk_duration_ms

            if not stop_on_silence:
                continue

            if self.vad.is_speech(chunk, SAMPLE_RATE):
                speech_started = True
                silence = 0
            elif speech_started and elapsed_ms > initial_silence_grace_ms:
                silence += 1

            if speech_started and silence * chunk_duration_ms > pause_threshold_ms:
                logger.debug(f"Silence detected after {elapsed_ms / 1000:.1f}s, recording stopped")
                break

            no_speech_timeout_ms = (self.cfg.vad.no_speech_timeout or 5.0) * 1000
            if not speech_started and elapsed_ms > no_speech_timeout_ms:
                logger.debug(f"No speech detected after {elapsed_ms / 1000:.1f}s, stopping")
                break

        return b"".join(recorded_audio_chunks)

    def stop_manual_recording(self):
        """Stop the manual recording by setting the stop flag."""
        if not self.recording_active:
            return

        self.stop_recording_flag = True

    def show_status_window(self, message, status_type="default", width=200, height=100):
        """Show a small status window centered on primary monitor"""

        assert self._color_style
        c = self.cfg.colors[self._color_style]
        bg_color = c.get(status_type, 'gray')

        def update_gui():
            try:
                if self.status_window:
                    self.status_window.configure(bg=bg_color)
                    for widget in self.status_window.winfo_children():
                        widget.destroy()
                else:
                    self.status_window = tk.Tk()
                    self.status_window.title("Dictation")
                    self.status_window.attributes("-topmost", True)
                    self.status_window.overrideredirect(True)

                    try:
                        from screeninfo import get_monitors

                        primary_monitor = next(m for m in get_monitors() if m.is_primary)
                        x = primary_monitor.x + (primary_monitor.width - width) // 2
                        y = primary_monitor.y + (primary_monitor.height - height) // 2
                        self.status_window.geometry(f"{width}x{height}+{x}+{y}")
                    except Exception:
                        self.status_window.geometry(f"{width}x{height}+860+490")

                    self.status_window.configure(bg=bg_color)

                tk.Label(
                    self.status_window,
                    text=message,
                    bg=bg_color,
                    fg=self._fg_color,
                    font=("Arial", 12),
                ).pack(expand=True)
                self.status_window.update()
            except tk.TclError as e:
                logger.warning(f"Status window disabled: {e}")
                self.status_window = None

        if threading.current_thread() is threading.main_thread():
            update_gui()
        else:
            self.gui_queue.append(update_gui)

    def hide_status_window(self):
        """Hide the status window"""

        def hide_gui():
            if self.status_window:
                self.status_window.destroy()
                self.status_window = None

        if threading.current_thread() is threading.main_thread():
            hide_gui()
        else:
            self.gui_queue.append(hide_gui)

    def _extract_local_path(self, text):
        """Extract filesystem paths from clipboard text (local and remote)."""
        if not text:
            return None

        # Look for user@host:/path or plain /path formats
        path_pattern = r'(?:(?P<host>[A-Za-z0-9._-]+@[A-Za-z0-9._-]+):)?(?P<path>/[^\s]+)'
        matches = re.finditer(path_pattern, text)

        # First, try to find local paths that exist
        for match in matches:
            candidate = match.group('path')
            if candidate.endswith('\\'):
                candidate = candidate[:-1]
            # Trim trailing punctuation
            candidate = candidate.rstrip('.,;')
            if os.path.exists(candidate):
                return candidate

        # If no local paths found, return the first remote SSH path found
        text = str(text)  # Ensure it's a string
        matches = re.finditer(path_pattern, text)
        for match in matches:
            full_path = match.group(0)  # Full match including host if present
            if '@' in full_path and ':' in full_path:
                # This is an SSH path
                return full_path

        # If no SSH paths, return the first path found even if it doesn't exist locally
        matches = re.finditer(path_pattern, text)
        for match in matches:
            candidate = match.group('path')
            if candidate.endswith('\\'):
                candidate = candidate[:-1]
            candidate = candidate.rstrip('.,;')
            if candidate and len(candidate) > 1:  # Ensure it's not just "/"
                return candidate

        return None

    def _prepare_prompt_inputs(self, raw_text, clipboard_context):
        """Normalize clipboard/raw text and extract useful context like filesystem paths."""
        processed_text = raw_text or ""
        processed_clipboard = clipboard_context or ""
        detected_path = self._extract_local_path(clipboard_context or "")

        if detected_path:
            logger.info(f"📂 Detected project path: {detected_path}")
            # Ensure clipboard context explicitly includes the usable path
            if processed_clipboard.strip() == "" or processed_clipboard.strip() == detected_path:
                processed_clipboard = detected_path
            elif detected_path not in processed_clipboard:
                processed_clipboard = f"{processed_clipboard.strip()}\n\nProject path: {detected_path}"

            # If clipboard mostly contained the path itself, create a clearer instruction
            if not processed_text.strip() or processed_text.strip() == clipboard_context.strip():
                processed_text = f"Please debug the system at {detected_path} and verify there are no outstanding issues."

        return processed_text, processed_clipboard, detected_path

    def _generate_ai_response(self, raw_text, clipboard_context=None):
        """Simple AI response generation - no complex pipelines."""
        if not raw_text:
            return None

        # Try to get clipboard if not provided
        if not clipboard_context:
            try:
                import subprocess
                result = subprocess.run(['xclip', '-selection', 'clipboard', '-o'],
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0 and result.stdout.strip():
                    clipboard_context = result.stdout.strip()
                    logger.info(f"📋 Retrieved clipboard context: {clipboard_context[:50]}...")
            except:
                pass

        original_voice_command = raw_text # Preserve original voice before RAG enhancement
        
        # 1. RAG Enhancement (Retrieve Context & Past Solutions)
        rag_context_info = ""
        if hasattr(self, 'rag_processor') and self.rag_processor and self.cfg.get('rag', {}).get('enabled', False):
            try:
                logger.info("🧠 Enhancing prompt with RAG (Past Solutions & File Context)")
                # Get current working directory as project root proxy
                cwd = os.getcwd()
                # We want RAG to return the "Context Info" separate from the voice,
                # but currently enhance_prompt returns a merged string.
                # For now, we will use the enhanced text as the 'past_patterns' context
                # and keep original_voice_command as the 'voice_input'.
                rag_enhanced_text = self.rag_processor.enhance_prompt(
                    raw_text,
                    context={
                        'clipboard': clipboard_context,
                        'project_root': cwd
                    }
                )
                
                # If RAG added something, extract it as context (simplified logic)
                if rag_enhanced_text != raw_text:
                    rag_context_info = rag_enhanced_text
                    # Note: We do NOT overwrite raw_text here with RAG output anymore for the Optimizer flow.
                    # We pass RAG output as 'past_patterns' argument.
            except Exception as e:
                logger.warning(f"⚠️ RAG enhancement failed: {e}")

        # Priority: Prompt Optimization (User request: optimize result as prompt)
        if self.prompt_optimizer:
            try:
                logger.info("✨ Optimizing result as prompt via AI")
                # 1. Construct the meta-prompt that tells AI how to structure the result
                # We pass the ORIGINAL VOICE as the primary command
                # We pass RAG info as 'past_patterns'
                meta_prompt = self.prompt_optimizer.construct_system_prompt_request(
                    voice_input=original_voice_command, 
                    clipboard=clipboard_context,
                    past_patterns=rag_context_info
                )
                
                # 2. Add a special flag/prefix so ai_processor knows this is a meta-request (optional, or just pass it)
                # But here we just pass the meta-prompt as the 'text' to process
                # We pass None as clipboard_context because the meta_prompt ALREADY includes the clipboard data inside it!
                
                if self.ai_processor:
                    logger.info("🤖 Sending meta-prompt to Smart AI Router")
                    optimized = self.ai_processor.process_dictation(meta_prompt, None)
                    if optimized:
                        logger.info(f"✅ AI Generated optimized prompt: {optimized[:50]}...")
                        return optimized
                    else:
                        logger.warning("⚠️ AI failed to generate prompt, falling back to rule-based")
                
                # Fallback to rule-based if AI fails or isn't available
                result = self.prompt_optimizer.optimize_prompt(raw_text, clipboard_context)
                if result and "optimized_prompt" in result:
                    return result["optimized_prompt"]
                    
            except Exception as e:
                logger.warning(f"⚠️ Prompt optimization failed: {e}")
                # Fallthrough to standard processing

        # Direct processing through Smart AI Router
        if self.ai_processor:
            logger.info("🤖 Simple AI processing with Smart Router")
            logger.info(f"   Text: '{raw_text[:50]}...'")
            logger.info(f"   Context: {'YES - ' + str(clipboard_context[:50]) + '...' if clipboard_context else 'NO'}")
            enhanced_text = self.ai_processor.process_dictation(raw_text, clipboard_context)
            logger.info(f"   Result: '{enhanced_text[:50]}...'" if enhanced_text else "No result")
            return enhanced_text
        else:
            logger.warning("⚠️ No AI processor available, returning original")
            return raw_text


    def start_manual_recording(self):
        """Start manual audio recording - records until stop command"""
        if self.recording_active:
            print("Recording already active")
            return

        self.recording_active = True

        def record_and_process():
            try:
                data = self.record_audio(60)
                self.show_status_window("Processing ⏳", "processing")
                audio = self._convert_raw_audio_to_sr_format(data)

                t = self._process_audio(audio)
                self.hide_status_window()
                if params.echo and self.cfg.general.get('echo_enabled', True):
                        self.speak_text(enhanced_text)
            except Exception as e:
                logger.error(f"Error during recording: {e}")
                logger.debug(traceback.format_exc())
                self._show_error("Recording error")
            finally:
                self.recording_active = False
                self.hide_status_window()

        threading.Thread(target=record_and_process, daemon=True).start()

    def start_ai_enhanced_recording(self, use_shift_enter=False):
        """Toggle AI-enhanced recording with Gemini processing"""
        print("🎯 DEBUG: start_ai_enhanced_recording called")
        logger.info("🎯 DEBUG: start_ai_enhanced_recording called - should read clipboard")

        if not self.gemini_processor:
            print("❌ Gemini API key not configured")
            self._show_error("❌ No API key")
            return

        # Toggle behavior: if recording, stop it
        if self.recording_active:
            print("Stopping AI recording")
            self.stop_recording_flag = True
            return

        self.recording_active = True

        def ai_record_and_process():
            try:
                data = self.record_audio(60)
                if not data or len(data) < 1000:
                    print("No audio recorded")
                    return

                self.show_status_window("AI Processing 🧠", "processing")
                audio = self._convert_raw_audio_to_sr_format(data)

                # Get recognized text
                raw_text = self._recognize(audio)
                if raw_text:
                    logger.info(f"Raw text: {raw_text}")

                    # Get clipboard content for context
                    clipboard_context = None
                    try:
                        import subprocess
                        result = subprocess.run(['xclip', '-selection', 'clipboard', '-o'],
                                              capture_output=True, text=True, timeout=2)
                        if result.returncode == 0 and result.stdout.strip():
                            clipboard_context = result.stdout.strip()
                            logger.info(f"📋 Clipboard context: {clipboard_context[:100]}...")
                            logger.info(f"📊 Clipboard length: {len(clipboard_context)} characters")
                    except Exception as e:
                        logger.error(f"❌ Could not get clipboard: {e}")

                    # Log what will be sent to AI
                    logger.info(f"🎤 Raw text: {raw_text}")
                    logger.info(f"🤖 Sending to AI processor with context: {'YES' if clipboard_context else 'NO'}")

                    enhanced_text = self._generate_ai_response(raw_text, clipboard_context)

                    logger.info(f"Enhanced text: {enhanced_text}")

                    # 3. Active Learning: Store successful pattern back to RAG
                    if enhanced_text and hasattr(self, 'rag_processor') and self.rag_processor:
                        try:
                            # Only store if meaningful change occurred
                            if enhanced_text != raw_text:
                                logger.info("🧠 Learning new pattern from successful interaction...")
                                self.rag_processor.store_successful_interaction(
                                    user_input=raw_text,
                                    ai_response=enhanced_text,
                                    user_feedback="implicit_success"
                                )
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to learn pattern: {e}")

                    self.hide_status_window()

                    # Check if we should type or copy to clipboard
                    if self.cfg.general.get('auto_type', True):
                        # Type the enhanced text - handle newlines
                        t = self.cfg.general.typewrite_interval or 0.05
                        lines = enhanced_text.split('\n')
                        for i, line in enumerate(lines):
                            if line.strip():
                                to_type = for_typewrite(self.curr_layout, line)
                                pyautogui.typewrite(to_type, interval=t)
                            if i < len(lines) - 1 and lines[i+1].strip():
                                if use_shift_enter:
                                    pyautogui.hotkey('shift', 'enter')
                                else:
                                    pyautogui.typewrite('\\', interval=t)
                                    pyautogui.press('enter')
                        pyautogui.typewrite(' ', interval=t)
                    else:
                        # Copy to clipboard instead of typing
                        try:
                            # Use xclip to copy to clipboard
                            subprocess.run(['xclip', '-selection', 'clipboard'],
                                         input=enhanced_text.encode(), check=True)

                            # Show ready notification
                            if self.cfg.general.get('show_ready_notification', True):
                                self._show_ready_notification(enhanced_text)

                            print(f"✅ Prompt ready to paste (Ctrl+V): {enhanced_text[:50]}...")

                        except Exception as e:
                            logger.error(f"Failed to copy to clipboard: {e}")
                            # Fallback to typing if clipboard fails
                            pyautogui.typewrite(enhanced_text, interval=0.05)

                    if params.echo and self.cfg.general.get('echo_enabled', True):
                        self.speak_text(enhanced_text)
                else:
                    self.hide_status_window()

            except sr.UnknownValueError:
                print("No speech detected")
            except Exception as e:
                logger.error(f"Error during AI recording: {e}")
                logger.debug(traceback.format_exc())
                self._show_error("AI processing error")
            finally:
                self.recording_active = False
                self.hide_status_window()

        threading.Thread(target=ai_record_and_process, daemon=True).start()

    def optimize_clipboard_prompt(self):
        """Optimize currently copied text and push result back to clipboard."""
        if not self.gemini_processor:
            print("❌ Gemini API key not configured")
            self._show_error("❌ No API key")
            return

        try:
            result = subprocess.run(
                ['xclip', '-selection', 'clipboard', '-o'],
                capture_output=True,
                text=True,
                timeout=2
            )
        except FileNotFoundError:
            logger.error("xclip not installed - clipboard optimization unavailable")
            self._show_error("Clipboard tool not found")
            return
        except Exception as e:
            logger.error(f"Failed to read clipboard: {e}")
            self._show_error("Clipboard read error")
            return

        if result.returncode != 0 or not result.stdout.strip():
            logger.info("Clipboard empty - nothing to optimize")
            self._show_error("Clipboard is empty")
            return

        clipboard_text = result.stdout.strip()
        logger.info(f"📋 Optimizing clipboard text ({len(clipboard_text)} chars)")

        self.show_status_window("Optimizing clipboard ✨", "processing")
        try:
            enhanced_text = self._generate_ai_response(clipboard_text, clipboard_text)
            if not enhanced_text:
                self._show_error("Clipboard optimization failed")
                return

            subprocess.run(
                ['xclip', '-selection', 'clipboard'],
                input=enhanced_text.encode(),
                check=True
            )

            if self.cfg.general.get('show_ready_notification', True):
                self._show_ready_notification(enhanced_text)

            print(f"✅ Optimized prompt ready (clipboard): {enhanced_text[:80]}{'...' if len(enhanced_text) > 80 else ''}")
        except Exception as e:
            logger.error(f"Error while optimizing clipboard text: {e}")
            self._show_error("Clipboard optimization error")
        finally:
            self.hide_status_window()

    def start_ai_clean_recording(self, use_shift_enter=False):
        """AI-enhanced recording WITHOUT clipboard context"""
        print("🧹 DEBUG: start_ai_clean_recording called - ignoring clipboard")
        logger.info("🧹 DEBUG: start_ai_clean_recording called - ignoring clipboard")

        if not self.gemini_processor:
            print("❌ Gemini API key not configured")
            self._show_error("❌ No API key")
            return

        if self.recording_active:
            print("Stopping AI recording")
            self.stop_recording_flag = True
            return

        self.recording_active = True

        def ai_clean_record_and_process():
            try:
                data = self.record_audio(60)
                if not data or len(data) < 1000:
                    print("No audio recorded")
                    return

                self.show_status_window("AI Processing 🧠", "processing")
                audio = self._convert_raw_audio_to_sr_format(data)

                raw_text = self._recognize(audio)
                if raw_text:
                    logger.info(f"Raw text: {raw_text}")

                    # Process through AI pipeline (clean context)
                    enhanced_text = self._generate_ai_response(raw_text, None)
                    logger.info(f"Enhanced text: {enhanced_text}")

                    self.hide_status_window()

                    # Check if we should type or copy to clipboard
                    if self.cfg.general.get('auto_type', True):
                        t = self.cfg.general.typewrite_interval or 0.05
                        lines = enhanced_text.split('\n')
                        for i, line in enumerate(lines):
                            if line.strip():
                                to_type = for_typewrite(self.curr_layout, line)
                                pyautogui.typewrite(to_type, interval=t)
                            if i < len(lines) - 1 and lines[i+1].strip():
                                if use_shift_enter:
                                    pyautogui.hotkey('shift', 'enter')
                                else:
                                    pyautogui.typewrite('\\', interval=t)
                                    pyautogui.press('enter')
                        pyautogui.typewrite(' ', interval=t)
                    else:
                        # Copy to clipboard instead of typing
                        try:
                            subprocess.run(['xclip', '-selection', 'clipboard'],
                                         input=enhanced_text.encode(), check=True)

                            if self.cfg.general.get('show_ready_notification', True):
                                self._show_ready_notification(enhanced_text)

                            print(f"✅ Prompt ready to paste (Ctrl+V): {enhanced_text[:50]}...")

                        except Exception as e:
                            logger.error(f"Failed to copy to clipboard: {e}")
                            pyautogui.typewrite(enhanced_text, interval=0.05)

                    if params.echo and self.cfg.general.get('echo_enabled', True):
                        self.speak_text(enhanced_text)
                else:
                    self.hide_status_window()

            except sr.UnknownValueError:
                print("No speech detected")
            except Exception as e:
                logger.error(f"Error during AI clean recording: {e}")
                logger.debug(traceback.format_exc())
                self._show_error("AI processing error")
            finally:
                self.recording_active = False
                self.hide_status_window()

        threading.Thread(target=ai_clean_record_and_process, daemon=True).start()

    def _recognize(self, audio):
        engine = self.recognizer_engines.get(self.recognizer_engine)
        config = dict(self.cfg[f"recognize_{self.recognizer_engine}"] or {})

        config["language"] = self.cur_lang
        logger.debug(f"Using recognition language: '{self.cur_lang}' for {self.curr_layout}")

        result = engine["recognize"](audio, **config)
        return engine["parser"](result)

    def _process_audio(self, audio):
        """Process audio through speech recognition and handle results"""
        logger.debug("")
        text = None
        try:
            text = self._recognize(audio)
            logger.info(text)

            # Check if we should type or copy to clipboard
            if self.cfg.general.get('auto_type', True):
                to_type = for_typewrite(self.curr_layout, text)
                t = self.cfg.general.typewrite_interval or 0.05
                pyautogui.typewrite(to_type + " ", interval=t)
            else:
                # Copy to clipboard instead of typing
                try:
                    subprocess.run(['xclip', '-selection', 'clipboard'],
                                 input=text.encode(), check=True)

                    if self.cfg.general.get('show_ready_notification', True):
                        self._show_ready_notification(text)

                    print(f"✅ Prompt ready to paste (Ctrl+V): {text[:50]}...")

                except Exception as e:
                    logger.error(f"Failed to copy to clipboard: {e}")
                    # Fallback to typing
                    to_type = for_typewrite(self.curr_layout, text)
                    pyautogui.typewrite(to_type + " ", interval=0.05)
        except sr.UnknownValueError:
            print("No speech detected")
            # self._show_error("No speech detected")
        except sr.RequestError as e:
            print(f"❌ Speech service error: {e}")
            self._show_error("❌ Service error")
        except Exception as e:
            print(f"❌ Recognition error: {e}")
            self._show_error("❌ Recognition error")
        return text

    def _convert_raw_audio_to_sr_format(self, data):
        """Convert raw audio data to speech_recognition AudioData format"""
        logger.debug("")
        import io
        import wave

        buf = io.BytesIO()
        with wave.open(buf, "wb") as f:
            f.setnchannels(CHANNELS)  # pylint: disable=no-member
            f.setsampwidth(SAMPLE_WIDTH)  # pylint: disable=no-member
            f.setframerate(SAMPLE_RATE)  # pylint: disable=no-member
            f.writeframes(data)  # pylint: disable=no-member
        buf.seek(0)
        return sr.AudioData(buf.getvalue(), SAMPLE_RATE, SAMPLE_WIDTH)

    def start_continuous_recording(self):
        """Start continuous audio recording - records until silence/pause detected"""
        logger.debug("")

        if self.recording_active or self.continuous_mode_active:
            print("Recording already active")
            return

        self.continuous_mode_active = True

        def continuous_record_and_process():
            try:
                print("Listening 🎤")
                while self.continuous_mode_active and not self.shutdown_flag:
                    data = self.record_audio(max_duration=60, stop_on_silence=True)

                    audio_duration = len(data) / BYTES_PER_SEC
                    print(f"Recorded {audio_duration:.2f} seconds of audio")

                    self.show_status_window("⏳ Processing...", "processing")
                    audio = self._convert_raw_audio_to_sr_format(data)

                    if not self._process_audio(audio):
                        print("Stopping")
                        self.continuous_mode_active = False
                        break

            except Exception as e:
                print(f"Failed during continuous recording: {e}")
                logger.debug(traceback.format_exc())
            finally:
                self.continuous_mode_active = False

        threading.Thread(target=continuous_record_and_process, daemon=True).start()

    def _show_error(self, message):
        """Show error window"""
        logger.debug(message)
        self.show_status_window(message, "error")

        def hide_later():
            time.sleep(2)
            logger.debug("")
            self.hide_status_window()

        threading.Thread(target=hide_later, daemon=True).start()

    def _toggle_recording(self):
        """Toggle manual recording on/off"""
        if self.recording_active:
            print("Stopping recording")
            self.stop_manual_recording()
        else:
            print("Starting recording")
            self.start_manual_recording()

    def _toggle_speech_echo(self):
        """Toggle speech echo on/off"""
        params.echo = not params.echo
        status = "enabled" if params.echo else "disabled"
        print(f"Speech echo {status}")
        self.show_status_window(f"Echo {status}", "echo")
        threading.Timer(1.0, self.hide_status_window).start()

    def input_command(self, fifo):
        """Read and process commands from the FIFO pipe."""
        if not fifo:
            try:
                fifo = os.fdopen(os.open(params.trigger, os.O_RDONLY | os.O_NONBLOCK), "r")
            except OSError as e:
                if e.errno == errno.ENXIO:  # No writer yet
                    time.sleep(0.1)
                else:
                    raise

        ready, _, _ = select.select([fifo], [], [], 0.5)
        if not ready:
            return
        line = fifo.readline().strip()
        if line:
            self.command = line
            logger.info(line)

            if self.command in self.commands:
                self.commands[self.command][0]()
            else:
                print(f"Unknown command: {line}")

    def run(self):
        """Start the FIFO listener"""
        if os.path.exists(params.trigger):
            os.remove(params.trigger)

        try:
            os.mkfifo(params.trigger)
            print(f"Created FIFO pipe: {params.trigger}")
        except OSError as e:
            print(f"Could not create FIFO pipe: {e}")
            return

        print("Commands:")
        for cmd, (_, description) in self.commands.items():
            print(f"  echo '{cmd}' > {params.trigger} # {description}")
        print("Press Ctrl+C to exit")
        logger.debug("Staring command loop")

        fifo = None
        try:
            while not self.shutdown_flag:
                while self.gui_queue:
                    self.gui_queue.pop(0)()

                self.input_command(fifo)
        finally:
            self._cleanup()

    def _cleanup(self):
        """Cleanup resources"""
        if self._cleaned_up:
            return
        self._cleaned_up = True

        print("\nCleaning up resources...")
        if os.path.exists(params.trigger):
            os.remove(params.trigger)
        self.hide_status_window()


def check_dependencies():
    """Check if required dependencies are available"""
    try:
        # Check if speech_recognition is already imported
        if "speech_recognition" not in sys.modules:
            import speech_recognition  # noqa: F401

        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install required packages:")
        print("pip install -r requirements.txt")
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Text Dictation Application")
    parser.add_argument(
        "--echo",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enable/disable echo to speak back the recognized text (default: enabled).",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode for detailed exception logging.",
    )
    parser.add_argument(
        "--calibrate",
        action="store_true",
        help="Run calibration to find the best speech recognition engine.",
    )
    parser.add_argument(
        "--trigger",
        type=str,
        default="/tmp/dictate_trigger",
        help="Custom FIFO trigger path (default: /tmp/dictate_trigger). "
        "When custom trigger is used, existing instances are not killed.",
    )
    global params
    params = parser.parse_args()

    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname).1s %(name)s:%(lineno)d: %(funcName)s %(message)s",
        datefmt="%H:%M:%S",
    )
    handler.setFormatter(formatter)
    logging.basicConfig(level=logging.DEBUG if params.debug else logging.INFO, handlers=[handler])
    if params.debug:
        for lib in ["gtts", "speech_recognition", "urllib3", "pydub"]:
            logging.getLogger(lib).setLevel(logging.INFO)

    pid_file = "/tmp/dictate.pid"

    # Only handle PID file if using default trigger
    if params.trigger == "/tmp/dictate_trigger" and os.path.exists(pid_file):
        try:
            with open(pid_file, "r") as f:
                pid = int(f.read().strip())
            print(f"Terminating previous instance with PID {pid}...")
            os.kill(pid, signal.SIGTERM)
            time.sleep(0.1)
        except (IOError, ValueError, ProcessLookupError):
            # Stale PID file or process not found
            pass
        except Exception as e:
            print(f"Error terminating previous instance: {e}")
            logger.debug(traceback.format_exc())

    try:
        if params.trigger == "/tmp/dictate_trigger":
            with open(pid_file, "w") as f:
                f.write(str(os.getpid()))

        if not check_dependencies():
            sys.exit(1)

        if sys.platform != "linux":
            print("This application is designed for Linux systems.")
            sys.exit(1)

        subprocess.run(["xhost", "+"], capture_output=True, check=False)

        app = DictationApp()
        signal.signal(signal.SIGINT, app.signal_handler)

        if params.calibrate:
            app.calibrate()
            sys.exit(0)

        try:
            app.run()
        except Exception as e:
            print(f"Error starting application: {e}")
            logger.debug(traceback.format_exc())
            sys.exit(1)

    finally:
        # Only cleanup PID file if using default trigger
        if params.trigger == "/tmp/dictate_trigger" and os.path.exists(pid_file):
            try:
                with open(pid_file, "r") as f:
                    if int(f.read().strip()) == os.getpid():
                        os.remove(pid_file)
            except (IOError, ValueError):
                pass  # Ignore errors on cleanup


if __name__ == "__main__":
    main()
