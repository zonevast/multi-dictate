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

import threading
import time
import tkinter as tk
import speech_recognition as sr
import pyautogui
import sys
import os
import select
import traceback
import yaml


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
                self.device_name = f"device {device_idx}: " f"{microphone_names[device_idx]}"
            else:
                self.device_name = f"device {device_idx}"

            print(f"Testing microphone: {self.device_name}")
            mic = sr.Microphone(device_index=device_idx)

            try:
                mic.stream = None
                with mic:
                    pass
                print(f"Using microphone: {self.device_name}")
                return mic
            except Exception as e:
                print(f"microphone {self.device_name} faied {e}")
                traceback.print_exc()
                mic = None
                continue

        return None

    def show_status_window(self, message, color="red", width=200, height=30):
        """Show a small status window"""

        def update_gui():
            if self.status_window:
                self.status_window.destroy()

            self.status_window = tk.Tk()
            self.status_window.title("Dictation")
            self.status_window.geometry(f"{width}x{height}+300+10")
            self.status_window.configure(bg=color)
            self.status_window.attributes("-topmost", True)
            self.status_window.overrideredirect(True)

            label = tk.Label(self.status_window, text=message, bg=color, fg="white", font=("Arial", 12))
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

    def start_recording(self):
        """Start audio recording and speech recognition"""

        def recorded_cb(recognizer, audio):
            self.show_status_window("⏳ Processing...", "orange")
            print("⏳ Processing...")

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
                print("No speech detected")
                self._show_error("No speech detected")
            except sr.RequestError as e:
                print(f"❌ Speech service error: {e}")
                self._show_error("❌ Service error")
            except Exception as e:
                print(f"❌ Recognition error: {e}")
                self._show_error("❌ Recognition error")


            if self.command == 'stop':
                self.stop_listening(wait_for_stop=False)
                self.hide_status_window()

        # start_recording
        if not self.microphone:
            print("Cannot record: No microphone available")
            return
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

        print(f"Commands: echo 'rec' > {fifo_path} or " f"echo 'stop' > {fifo_path}")
        print("Press Ctrl+C to exit")

        try:
            with open("/tmp/dictate_trigger", "r") as fifo:
                while True:
                    try:
                        # Process GUI queue
                        while self.gui_queue:
                            gui_update = self.gui_queue.pop(0)
                            gui_update()

                        # Check if FIFO has data with timeout
                        ready, a, b = select.select([fifo], [], [], 0.1)
                        if ready:
                            line = fifo.readline().strip()
                            if line:
                                self.command = line
                                print(f" >>> {line}")
                            elif line:
                                print(f"Unknown command: {line}")
                            if self.command == 'rec':
                                self.show_status_window("🎤 Recording...", "red")
                                if not self.microphone.stream:
                                    self.command = None
                                    self.start_recording()

                    except KeyboardInterrupt:
                        break
                    except Exception as e:
                        print(f"FIFO read error: {e}")
                    finally:
                        time.sleep(0.1)

        except KeyboardInterrupt:
            print("\nExiting...")
        finally:
            if os.path.exists("/tmp/dictate_trigger"):
                os.remove("/tmp/dictate_trigger")
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
