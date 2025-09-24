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

import os
import select
import signal
import sys
import threading
import time
import tkinter as tk
import traceback

import pasimple
import pyautogui
import yaml

import speech_recognition as sr

FORMAT = pasimple.PA_SAMPLE_S32LE
SAMPLE_WIDTH = pasimple.format2width(FORMAT)
CHANNELS = 1
SAMPLE_RATE = 44100
BYTES_PER_SEC = CHANNELS * SAMPLE_RATE * SAMPLE_WIDTH


class DictationApp:
    def __init__(self):
        config = {}
        try:
            with open("dictate.yaml", "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except Exception:
            pass
        self.status_window = None
        self.show_status_window("Starting", "blue")
        self.recognizer = sr.Recognizer()
        vars(self.recognizer).update(config.get("Recognizer", {}))
        self.microphone = self.setup_microphone()
        if not self.microphone:
            print("ERROR: No working microphone found")

        self.gui_queue = []
        self.command = None
        self.pasimple_stream = None
        self.recording_active = False
        self.stop_recording_flag = False
        self.recorded_audio_chunks = []

        # Command mapping
        self.commands = {
            "record": (self.start_manual_recording, "Start manual recording till stop"),
            "stop": (self.stop_manual_recording, "Stop manual recording"),
            "toggle": (self._toggle_recording, "Toggle manual recording"),
            "record till pause": (self.start_continuous_recording, "Start continuous recording till audio pause"),
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
                print(f"microphone {self.device_name} faied {e}")
                traceback.print_exc()
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
        self._log_stream_info()
        return True

    def _log_stream_info(self):
        """Log pasimple stream information"""
        print(f"Audio stream: {self.pasimple_stream.channels()}ch {self.pasimple_stream.rate()}Hz")

    def record_audio(self, max_duration=60):
        """Record audio manually until stop command or timeout"""
        if not self.pasimple_stream:
            try:
                self.setup_pasimple_recording()
            except Exception as e:
                print(f"Failed to setup recording: {e}")
                return None

        self.recorded_audio_chunks = []
        self.stop_recording_flag = False

        try:
            return self._record_chunks(BYTES_PER_SEC // 10, max_duration * 10, max_duration)
        except Exception as e:
            print(f"Recording failed: {e}")
            return None

    def _record_chunks(self, chunk_size, total_chunks, max_duration):
        """Record audio chunks in a loop"""
        for chunk_num in range(total_chunks):
            if self.stop_recording_flag:
                break

            if chunk_num % 10 == 0:
                elapsed = chunk_num * 0.1
                self.show_status_window(f"🎤 Recording... {elapsed:.0f}s", "red")

            chunk = self.pasimple_stream.read(chunk_size)
            self.recorded_audio_chunks.append(chunk)

        return b"".join(self.recorded_audio_chunks)

    def _combine_audio_chunks(self):
        """Combine recorded audio chunks into single audio data"""
        if not self.recorded_audio_chunks:
            return None

    def stop_manual_recording(self):
        if not self.recording_active:
            return

        self.stop_recording_flag = True

    def show_status_window(self, message, color="red", width=300, height=20):
        """Show a small status window centered on primary monitor"""

        def update_gui():
            if self.status_window:
                self.status_window.destroy()

            self.status_window = tk.Tk()
            self.status_window.title("Dictation")
            self.status_window.configure(bg=color)
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

            label = tk.Label(
                self.status_window,
                text=message,
                bg=color,
                fg="white",
                font=("Arial", 12),
            )
            label.pack(expand=True)
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
        self.show_status_window("🎤 Recording...", "red")

        def record_and_process():
            try:
                data = self.record_audio(60)
                if not data:
                    self._show_error("Recording failed")
                    return

                self.show_status_window("⏳ Processing...", "orange")

                audio = self._convert_raw_audio_to_sr_format(data)
                if not audio:
                    self._show_error("Audio conversion failed")
                    return

                self._process_speech_recognition(audio)
            finally:
                self.recording_active = False

        threading.Thread(target=record_and_process, daemon=True).start()

    def _process_recorded_audio(self, recognizer, audio):
        """Process recorded audio in separate thread"""
        try:
            text = recognizer.recognize_google(audio)
            print(f"> {text}")
            self.show_status_window(text, "green")

            def hide_later():
                time.sleep(3)
                self.hide_status_window()

            threading.Thread(target=hide_later, daemon=True).start()
            pyautogui.typewrite(text + " ")
        except sr.UnknownValueError:
            self.command = "stop"
            print("No speech detected")
            self._show_error("No speech detected")
        except sr.RequestError as e:
            print(f"❌ Speech service error: {e}")
            self._show_error("❌ Service error")
        except Exception as e:
            print(f"❌ Recognition error: {e}")
            self._show_error("❌ Recognition error")

        if self.command == "stop":
            self.stop_listening(wait_for_stop=False)
            self.hide_status_window()

    def _convert_raw_audio_to_sr_format(self, data):
        """Convert raw audio data to speech_recognition AudioData format"""
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
            return None

    def _process_speech_recognition(self, audio):
        """Process audio through speech recognition and handle results"""
        try:
            text = self.recognizer.recognize_google(audio)
            print(f"> {text}")
            self.show_status_window(text, "green")

            def hide_later():
                time.sleep(3)
                self.hide_status_window()

            threading.Thread(target=hide_later, daemon=True).start()
            pyautogui.typewrite(text + " ")
        except sr.UnknownValueError:
            print("No speech detected")
            self._show_error("No speech detected")
        except sr.RequestError as e:
            print(f"❌ Speech service error: {e}")
            self._show_error("❌ Service error")
        except Exception as e:
            print(f"❌ Recognition error: {e}")
            self._show_error("❌ Recognition error")

    def start_continuous_recording(self):
        """Start continuous audio recording - records until silence/pause detected"""

        def recorded_cb(recognizer, audio):
            self.show_status_window("⏳ Processing...", "orange")
            threading.Thread(
                target=self._process_recorded_audio,
                args=(recognizer, audio),
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
        self.show_status_window("🎤 Recording...", "red")
        try:
            self.stop_listening = self.recognizer.listen_in_background(self.microphone, recorded_cb)
            print(f"🔴 Recording with {self.device_name}")
        except Exception as e:
            print(f"Failed to start background listening: {e}")

    def _show_error(self, message):
        """Show error window"""
        self.show_status_window(message, "red")

        # Auto-hide after 2 seconds
        def hide_later():
            time.sleep(2)
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

    def input_command(self, fifo):
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

        fifo_path = "/tmp/dictate_trigger"
        if os.path.exists(fifo_path):
            os.remove(fifo_path)

        try:
            os.mkfifo(fifo_path)
            print(f"Created FIFO pipe: {fifo_path}")
        except OSError as e:
            print(f"Could not create FIFO pipe: {e}")
            return

        print(f"Commands:")
        for cmd, (_, description) in self.commands.items():
            print(f"  echo '{cmd}' > {fifo_path} # {description}")
        print("Press Ctrl+C to exit")

        try:
            with open(fifo_path, "r") as fifo:
                while True:
                    try:
                        # Process GUI queue
                        while self.gui_queue:
                            gui_update = self.gui_queue.pop(0)
                            gui_update()

                        # Use select with longer timeout for efficiency
                        ready, _, _ = select.select([fifo], [], [], 1.0)
                        if ready:
                            self.input_command(fifo)

                    except KeyboardInterrupt:
                        break
                    except Exception as e:
                        print(f"FIFO read error: {e}")

        except KeyboardInterrupt:
            print("\nExiting...")
        finally:
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
    if not check_dependencies():
        sys.exit(1)

    if sys.platform != "linux":
        print("This application is designed for Linux systems.")
        sys.exit(1)

    try:
        app = DictationApp()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
