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
import pyautogui
import speech_recognition as sr

warnings.filterwarnings("ignore", category=UserWarning, module="webrtcvad")
import webrtcvad
import yaml
from box import Box
from gtts import gTTS
from pydub import AudioSegment
from vosk import SetLogLevel

from kbd_utils import for_typewrite, get_current_keyboard_layout, kbd_cfg

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
        try:
            with open("dictate.yaml", "r", encoding="utf-8") as f:
                y = yaml.safe_load(f) or {}
        except Exception:
            logger.debug(traceback.format_exc())
        self.cfg = Box(y, default_box=True)
        self.recognizer_engine = self.cfg.general.recognizer_engine or "google"
        self.status_window = None
        self.recognizer = sr.Recognizer()
        self.vad = webrtcvad.Vad()
        self.curr_layout = None
        self.vad.set_mode(self.cfg.vad.aggressiveness or 0)  # Set aggressiveness mode (0-3)
        vars(self.recognizer).update(self.cfg.Recognizer)

        self.recognizer_engines = {
            "google": {
                "recognize": self.recognizer.recognize_google,
                "parser": lambda result: result,
            },
            "vosk": {
                "recognize": self.recognizer.recognize_vosk,
                "parser": lambda result: json.loads(result).get("text", ""),
            },
        }

        self.gui_queue = []
        self.command = None
        self.pasimple_stream = None
        self.recording_active = False
        self.stop_recording_flag = False
        self.continuous_mode_active = False
        self.shutdown_flag = False
        self._cleaned_up = False

        # Command mapping
        self.commands = {
            "record": (self.start_manual_recording, "Start manual recording till stop"),
            "stop": (self.stop_manual_recording, "Stop manual recording"),
            "toggle": (self._toggle_recording, "Toggle manual recording"),
            "record till pause": (
                self.start_continuous_recording,
                "Start continuous recording till audio pause",
            ),
            "echo": (self._toggle_speech_echo, "Toggle speech echo on/off"),
        }

        self.setup_pasimple_recording()
        self.tts_lock = threading.Lock()

    def calibrate(self):

        import Levenshtein

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
        if not audio:
            print("Calibration failed: Audio conversion error.")
            return

        results = []
        print("Recognizing")
        for engine_name, engine_details in self.recognizer_engines.items():
            print(f"  {engine_name}")
            try:
                config = dict(self.cfg[f"recognize_{engine_name}"] or {})
                user = engine_details["parser"](engine_details["recognize"](audio, **config))
                dist = Levenshtein.distance(re.sub(r"[^\w\s]", "", orig).lower(), user)
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
        """Setup pasimple audio recording stream"""
        self.pasimple_stream = pasimple.PaSimple(
            pasimple.PA_STREAM_RECORD,
            FORMAT,
            CHANNELS,
            SAMPLE_RATE,
            app_name="dictate-app",
            stream_name="record-mono",
            maxlength=BYTES_PER_SEC * 2,
            fragsize=BYTES_PER_SEC // 5,
        )
        return True

    def _speak_with_gtts(self, text):
        """Try to speak text using gTTS and pasimple."""
        try:
            # Get gTTS config and override language if auto-detection is enabled
            gtts_config = (self.cfg.gTTS or {}).copy()
            if gtts_config.get("lang", "auto").lower() == "auto":
                gtts_config["lang"] = (
                    kbd_cfg.layouts[self.curr_layout].languages.tts or self.curr_layout
                )
                logger.debug(f"Using TTS language: {gtts_config['lang']}")

            # Generate audio with gTTS
            logger.debug(gtts_config)
            tts = gTTS(text, **gtts_config)
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)

            # Decode MP3 with pydub
            audio = AudioSegment.from_mp3(audio_buffer)
            audio -= 20  # Reduce volume by 20 dB

            logger.debug(
                f"Decoded audio: {audio.channels} channels, "
                f"{audio.frame_rate} Hz, {len(audio.raw_data)} bytes"
            )

            # Play audio with pasimple
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

    def record_audio(self, max_duration=60, stop_on_silence=False):
        """Record audio manually until stop command or timeout"""
        if not self.pasimple_stream:
            print("Failed to setup recording")
            return None

        self.stop_recording_flag = False

        self.curr_layout = get_current_keyboard_layout()
        self.cur_lang = (self.cfg[f"recognize_{self.recognizer_engine}"].language or "auto").lower()
        if self.cur_lang == "auto":
            self.cur_lang = (
                kbd_cfg.layouts[self.curr_layout].languages.stt
                or f"{self.curr_layout}-{self.curr_layout.upper()}"
            )

        # see _recognize
        if (self.cfg.recognize_google.language or "auto").lower() == "auto":
            lc = self.cur_lang.split("-")[0].upper()
            lc2 = f"{lc} " if lc != "EN" else ""
        else:
            lc2 = ""

        self.show_status_window(f"Listening {lc2}🎤", "lightcoral")

        try:
            return self._record_chunks(max_duration, stop_on_silence)
        except Exception as e:
            print(f"Recording failed: {e}")
            logger.debug(traceback.format_exc())
            return None
        finally:
            self.hide_status_window()

    def _record_chunks(self, max_duration, stop_on_silence=False):
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

            chunk = self.pasimple_stream.read(vad_chunk_size)

            recorded_audio_chunks.append(chunk)
            elapsed_ms = chunk_num * chunk_duration_ms

            if not stop_on_silence:
                continue

            # Update speech and silence tracking
            if self.vad.is_speech(chunk, SAMPLE_RATE):
                speech_started = True
                silence = 0
            elif speech_started and elapsed_ms > initial_silence_grace_ms:
                silence += 1

            # Check stopping conditions
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

    def show_status_window(self, message, color="lightcoral", width=300, height=20):
        """Show a small status window centered on primary monitor"""

        def update_gui():
            if self.status_window:
                # Update existing window instead of destroying
                self.status_window.configure(bg=color)
                for widget in self.status_window.winfo_children():
                    widget.destroy()
            else:
                self.status_window = tk.Tk()
                self.status_window.title("Dictation")
                self.status_window.attributes("-topmost", True)
                self.status_window.overrideredirect(True)

                # Center on primary monitor
                try:
                    from screeninfo import get_monitors

                    primary_monitor = next(m for m in get_monitors() if m.is_primary)
                    x = primary_monitor.x + (primary_monitor.width - width) // 2
                    y = primary_monitor.y + (primary_monitor.height - height) // 2
                    self.status_window.geometry(f"{width}x{height}+{x}+{y}")
                except Exception:
                    # Fallback to fixed position if screeninfo not available
                    self.status_window.geometry(f"{width}x{height}+300+10")

                self.status_window.configure(bg=color)

            tk.Label(
                self.status_window,
                text=message,
                bg=color,
                fg="black",
                font=("Arial", 12),
            ).pack(expand=True)
            self.status_window.update()

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

    def start_manual_recording(self):
        """Start manual audio recording - records until stop command"""
        if self.recording_active:
            print("Recording already active")
            return

        self.recording_active = True

        def record_and_process():
            try:
                data = self.record_audio(60)
                if not data:
                    self._show_error("Recording failed")
                    return

                self.show_status_window("Processing ⏳", "lightsalmon")

                audio = self._convert_raw_audio_to_sr_format(data)
                if not audio:
                    self.hide_status_window()
                    self._show_error("Audio conversion failed")
                    return

                t = self._process_audio(audio)
                self.hide_status_window()
                if params.echo:
                    self.speak_text(t)
            finally:
                self.recording_active = False
                self.hide_status_window()

        threading.Thread(target=record_and_process, daemon=True).start()

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

            # Convert the recognized text to physical keys for the current layout
            to_type = for_typewrite(text, self.curr_layout)
            t = self.cfg.general.typewrite_interval or 0.05
            pyautogui.typewrite(to_type + " ", interval=t)
        except sr.UnknownValueError:
            print("No speech detected")
            self._show_error("No speech detected")
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
        try:
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

        except Exception as e:
            print(f"Audio conversion error: {e}")
            logger.debug(traceback.format_exc())
            return None

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
                    # Record audio until silence is detected
                    data = self.record_audio(max_duration=60, stop_on_silence=True)
                    if not data:
                        print("No audio data recorded")
                        continue

                    # Debug: show audio length
                    audio_duration = len(data) / BYTES_PER_SEC
                    print(f"Recorded {audio_duration:.2f} seconds of audio")

                    self.show_status_window("⏳ Processing...", "lightsalmon")

                    audio = self._convert_raw_audio_to_sr_format(data)
                    if not audio:
                        logger.error("Audio conversion failed")
                        break

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
        logger.debug("")
        self.show_status_window(message, "lightcoral")

        # Auto-hide after 2 seconds
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
        self.show_status_window(f"Echo {status}", "lightblue")

    def input_command(self, fifo):
        """Read and process commands from the FIFO pipe."""
        # Wait for data on the fifo with a timeout
        if not fifo:
            try:
                # Use non-blocking open to avoid getting stuck
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
                # Process GUI queue
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
        if self.pasimple_stream:
            self.pasimple_stream = None  # Allow garbage collection
        if os.path.exists(params.trigger):
            os.remove(params.trigger)
        self.hide_status_window()


def check_dependencies():
    """Check if required dependencies are available"""
    try:
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
            time.sleep(0.1)  # Give it a moment to terminate
        except (IOError, ValueError, ProcessLookupError):
            # Stale PID file or process not found
            pass
        except Exception as e:
            print(f"Error terminating previous instance: {e}")
            logger.debug(traceback.format_exc())

    try:
        # Only write PID file if using default trigger
        if params.trigger == "/tmp/dictate_trigger":
            with open(pid_file, "w") as f:
                f.write(str(os.getpid()))

        if not check_dependencies():
            sys.exit(1)

        if sys.platform != "linux":
            print("This application is designed for Linux systems.")
            sys.exit(1)

        # Allow X11 connections
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
