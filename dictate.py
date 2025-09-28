#!/usr/bin/env python3
"""
Fedora Linux Text Dictation Application

Activates with hotkey, records audio, converts to text using Google Speech
Recognition, and pastes the result into the current input field.

main
    run
        __init__
            listen_in_background -> speech_recognition
                recorded_cb
                    recognize_google -> speech_recognition
                    insert_text
                        typewrite -> pyautogui

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

import Levenshtein
import pasimple
import pyautogui
import speech_recognition as sr
import yaml
from gtts import gTTS
from vosk import SetLogLevel

SetLogLevel(-1)

FORMAT = pasimple.PA_SAMPLE_S32LE
SAMPLE_WIDTH = pasimple.format2width(FORMAT)
CHANNELS = 1
SAMPLE_RATE = 44100
BYTES_PER_SEC = CHANNELS * SAMPLE_RATE * SAMPLE_WIDTH

params = None
logger = logging.getLogger(os.path.basename(__file__))
fifo_path = "/tmp/dictate_trigger"


class DictationApp:
    def __init__(self):
        self.config = {}
        try:
            with open("dictate.yaml", "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}
        except Exception:
            logger.debug(traceback.format_exc())
            pass
        self.recognizer_engine = self.config.get("general", {}).get("recognizer_engine", "google")
        self.status_window = None
        self.show_status_window("Starting", "lightblue")
        self.recognizer = sr.Recognizer()
        vars(self.recognizer).update(self.config.get("Recognizer", {}))

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

        self.microphone = self.setup_microphone()
        if not self.microphone:
            print("ERROR: No working microphone found")

        self.gui_queue = []
        self.command = None
        self.pasimple_stream = None
        self.recording_active = False
        self.stop_recording_flag = False
        self.recorded_audio_chunks = []
        self.continuous_mode_active = False
        self.shutdown_flag = False

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

        # Configure speech recognition if microphone is available
        if self.microphone:
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source)
                    print("Audio calibration complete")
            except Exception as e:
                print(f"Audio calibration failed: {e}")
        else:
            print("WARNING: No microphone available")

        self.hide_status_window()

        print("Dictation app initialized.")

    def calibrate(self):
        """Calibrate voice recognition with all available engines."""
        intro = "Say this text for calibration of voice recognition during 20 seconds:"
        orig = "This quick voice checks sharp sounds, tests warm tone, and sings with vision."
        print("Calibration")
        print(f" {intro}\n\n\u001b[1m{orig}\u001b[0m")
        self.speak_text(intro + orig, sync=True)

        print("Recording 🎤")
        audio = self._convert_raw_audio_to_sr_format(self.record_audio(20))
        self.hide_status_window()
        self.speak_text("Thank you.")
        if not audio:
            print("Calibration failed: Audio conversion error.")
            return

        results = []
        print("Recognizing")
        for engine_name, engine_details in self.recognizer_engines.items():
            print(f"  {engine_name}")
            try:
                config = self.config.get(f"recognize_{engine_name}", {})
                user = engine_details["parser"](engine_details["recognize"](audio, **config))
                dist = Levenshtein.distance(re.sub(r"[^\w\s]", "", orig).lower(), user)
                results.append({"engine": engine_name, "text": user, "dist": dist})
                print(f"    Recognized: '{user}'")
                print(f"    Distance: {dist} (lower is better)")
            except Exception as e:
                print(f"    Error with {engine_name}: {e}")
                results.append({"engine": engine_name, "text": "Error", "dist": float("inf")})

        results.sort(key=lambda x: x["dist"])

        if results:
            print(f"Recommended: {results[0]['engine']}")
        else:
            print("\nCould not determine the best engine.")

    def signal_handler(self, sig, frame):
        """Handle SIGINT gracefully."""
        print("\nCaught Ctrl+C, shutting down...")
        self.shutdown_flag = True

    def setup_microphone(self):
        """Initialize microphone with fallback to multiple device indices."""
        microphone_names = sr.Microphone.list_microphone_names()
        print("Available microphones:")
        for index, name in enumerate(microphone_names):
            print(f"  {index}: {name}")

        mic = None
        for device_idx in [None, 1, 0, 2]:
            # Get the actual device name if available
            if device_idx is None:
                self.device_name = "default"
            elif device_idx < len(microphone_names):
                self.device_name = f"device {device_idx}: {microphone_names[device_idx]}"
            else:
                self.device_name = f"device {device_idx}"

            print(f"Testing microphone: {self.device_name}")
            mic = sr.Microphone(device_index=device_idx)

            try:
                mic.stream = None
                with mic:
                    """
                    get_default_input_device_info
                        get_default_input_device PyAudio_GetDefaultInputDevice
                            Pa_GetDefaultInputDevice
                                defaultInputDevice
                        Pa_GetDefaultHostApi
                            defaultHostApiIndex_
                    """
                    pass
                print(f"Using microphone: {self.device_name}")
                return mic
            except Exception as e:
                print(f"microphone {self.device_name} failed {e}")
                logger.debug(traceback.format_exc())
                mic = None
                continue

        return None

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

    def speak_text(self, text, sync=False):
        """Convert text to speech using gTTS with fallbacks"""
        logger.debug(f"'{text}'")
        if not text or not params.echo:
            return

        def speak_in_thread():
            try:
                warnings.filterwarnings("ignore", message="pkg_resources is deprecated as an API")
                os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
                import pygame

                tts = gTTS(text, **self.config.get("gTTS", {}))
                audio_buffer = BytesIO()
                tts.write_to_fp(audio_buffer)
                audio_buffer.seek(0)

                # Try different audio drivers for compatibility
                audio_drivers = [
                    {},  # Default settings
                    {"frequency": 22050, "size": -16, "channels": 2, "buffer": 512},
                    {"frequency": 44100, "size": -16, "channels": 1, "buffer": 1024},
                ]

                mixer_initialized = False
                for audio_config in audio_drivers:
                    try:
                        pygame.mixer.init(**audio_config)
                        mixer_initialized = True
                        break
                    except pygame.error:
                        continue

                if not mixer_initialized:
                    raise pygame.error("Could not initialize audio")

                pygame.mixer.music.load(audio_buffer)
                pygame.mixer.music.set_volume(0.1)
                pygame.mixer.music.play()

                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)

                if pygame.mixer.get_init():
                    pygame.mixer.quit()

            except Exception as e:
                print(f"TTS with pygame failed: {e}")
                logger.debug(traceback.format_exc())
                # Fallback to system TTS
                try:
                    subprocess.run(["espeak", "-a", "10", text], check=True, capture_output=True)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    try:
                        subprocess.run(["spd-say", text], check=True, capture_output=True)
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        print(f"TTS failed: {e}")

        if sync:
            speak_in_thread()
        else:
            threading.Thread(target=speak_in_thread, daemon=True).start()

    def record_audio(self, max_duration=60):
        """Record audio manually until stop command or timeout"""
        if not self.pasimple_stream:
            try:
                self.setup_pasimple_recording()
            except Exception as e:
                print(f"Failed to setup recording: {e}")
                logger.debug(traceback.format_exc())
                return None

        self.recorded_audio_chunks = []
        self.stop_recording_flag = False

        try:
            return self._record_chunks(BYTES_PER_SEC // 10, max_duration * 10, max_duration)
        except Exception as e:
            print(f"Recording failed: {e}")
            logger.debug(traceback.format_exc())
            return None

    def _record_chunks(self, chunk_size, total_chunks, max_duration):
        """Record audio chunks in a loop"""
        logger.debug("")
        for chunk_num in range(total_chunks):
            if self.stop_recording_flag:
                break

            if chunk_num % 10 == 0:
                elapsed = chunk_num * 0.1
                self.show_status_window(f"🎤 Recording... {elapsed:.0f}s", "lightcoral")

            self.recorded_audio_chunks.append(self.pasimple_stream.read(chunk_size))

        return b"".join(self.recorded_audio_chunks)

    def stop_manual_recording(self):
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
            self.gui_queue.append(lambda: update_gui())

    def hide_status_window(self):
        """Hide the status window"""

        def hide_gui():
            if self.status_window:
                self.status_window.destroy()
                self.status_window = None

        if threading.current_thread() is threading.main_thread():
            hide_gui()
        else:
            self.gui_queue.append(lambda: hide_gui())

    def start_manual_recording(self):
        """Start manual audio recording - records until stop command"""
        if self.recording_active:
            print("Recording already active")
            return

        self.recording_active = True
        self.show_status_window("🎤 Recording...", "lightcoral")

        def record_and_process():
            try:
                data = self.record_audio(60)
                if not data:
                    self._show_error("Recording failed")
                    return

                self.show_status_window("⏳ Processing...", "lightsalmon")

                audio = self._convert_raw_audio_to_sr_format(data)
                if not audio:
                    self._show_error("Audio conversion failed")
                    return

                self._process_audio(audio, continuous=False)
            finally:
                self.recording_active = False

        threading.Thread(target=record_and_process, daemon=True).start()

    def _recognize(self, audio):
        engine = self.recognizer_engines.get(self.recognizer_engine)
        config = self.config.get(f"recognize_{self.recognizer_engine}", {})
        result = engine["recognize"](audio, **config)
        return engine["parser"](result)

    def _process_audio(self, audio, continuous=False):
        """Process audio through speech recognition and handle results"""
        logger.debug("")
        text = None
        try:
            text = self._recognize(audio)
            print(f"> {text}")
            self.show_status_window(text, "lightgreen")

            def hide_later():
                logger.debug("")
                time.sleep(3)
                self.hide_status_window()

            threading.Thread(target=hide_later, daemon=True).start()
            pyautogui.typewrite(text + " ")
            if not continuous:
                self.speak_text(text)
        except sr.UnknownValueError:
            print("No speech detected")
            self._show_error("No speech detected")
        except sr.RequestError as e:
            print(f"❌ Speech service error: {e}")
            self._show_error("❌ Service error")
        except Exception as e:
            print(f"❌ Recognition error: {e}")
            self._show_error("❌ Recognition error")
        finally:
            if continuous and not text:
                self.command = "stop"

        if continuous:
            if self.command == "stop":
                print("Stopping")
                self.stop_listening(wait_for_stop=False)
                self.continuous_mode_active = False
                self.hide_status_window()
            elif self.continuous_mode_active:
                # Keep showing listening status in continuous mode
                self.show_status_window("🎤 Listening...", "lightcoral")
        else:
            self.speak_text(text)

    def _convert_raw_audio_to_sr_format(self, data):
        """Convert raw audio data to speech_recognition AudioData format"""
        logger.debug("")
        try:
            import io
            import wave

            buf = io.BytesIO()
            with wave.open(buf, "wb") as f:
                f.setnchannels(CHANNELS)
                f.setsampwidth(SAMPLE_WIDTH)
                f.setframerate(SAMPLE_RATE)
                f.writeframes(data)
            buf.seek(0)
            return sr.AudioData(buf.getvalue(), SAMPLE_RATE, SAMPLE_WIDTH)

        except Exception as e:
            print(f"Audio conversion error: {e}")
            logger.debug(traceback.format_exc())
            return None

    def start_continuous_recording(self):
        """Start continuous audio recording - records until silence/pause detected"""
        logger.debug("")

        def recorded_cb(_, audio):
            logger.debug("")
            self.show_status_window("⏳ Processing...", "lightsalmon")
            threading.Thread(
                target=self._process_audio,
                args=(audio, True),
                daemon=True,
            ).start()
            # Return immediately to caller

        # start_recording
        if not self.microphone:
            print("Cannot record: No microphone available")
            return
        if self.microphone.stream:
            # already recording
            return
        self.continuous_mode_active = True
        self.show_status_window("🎤 Listening...", "lightcoral")
        try:
            self.stop_listening = self.recognizer.listen_in_background(self.microphone, recorded_cb)
            print(f"🔴 Recording with {self.device_name}")
        except Exception as e:
            print(f"Failed to start background listening: {e}")
            logger.debug(traceback.format_exc())
            self.continuous_mode_active = False

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
        # Wait for data on the fifo with a timeout
        if not fifo:
            try:
                # Use non-blocking open to avoid getting stuck
                fifo = os.fdopen(os.open(fifo_path, os.O_RDONLY | os.O_NONBLOCK), "r")
            except OSError as e:
                if e.errno == errno.ENXIO:  # No writer yet
                    time.sleep(0.1)
                    return
                else:  # Other OS error
                    raise  # Other OS error

        ready, _, _ = select.select([fifo], [], [], 0.5)
        if not ready:
            return
        line = fifo.readline().strip()
        if line:
            self.command = line
            print(f" >>> {line}")

            if self.command in self.commands:
                self.commands[self.command][0]()
            else:
                print(f"Unknown command: {line}")

    def run(self):
        """Start the FIFO listener"""
        print("Dictation app is running...")

        if os.path.exists(fifo_path):
            os.remove(fifo_path)

        try:
            os.mkfifo(fifo_path)
            print(f"Created FIFO pipe: {fifo_path}")
        except OSError as e:
            print(f"Could not create FIFO pipe: {e}")
            return

        print("Commands:")
        for cmd, (_, description) in self.commands.items():
            print(f"  echo '{cmd}' > {fifo_path} # {description}")
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
            print("\nExiting...")
            if fifo:
                fifo.close()
            if os.path.exists(fifo_path):
                os.remove(fifo_path)
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
        for lib in ["gtts", "speech_recognition", "urllib3"]:
            logging.getLogger(lib).setLevel(logging.INFO)

    pid_file = "/tmp/dictate.pid"

    if os.path.exists(pid_file):
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
        with open(pid_file, "w") as f:
            f.write(str(os.getpid()))

        if not check_dependencies():
            sys.exit(1)

        if sys.platform != "linux":
            print("This application is designed for Linux systems.")
            sys.exit(1)

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
        if os.path.exists(pid_file):
            try:
                with open(pid_file, "r") as f:
                    if int(f.read().strip()) == os.getpid():
                        os.remove(pid_file)
            except (IOError, ValueError):
                pass  # Ignore errors on cleanup


if __name__ == "__main__":
    main()
