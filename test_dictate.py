#!/usr/bin/env python3
"""Test dictate.py speech recognition functionality."""
import os
import subprocess
import sys
import time
import tkinter as tk

import pyautogui

# Configuration
FIFO_PATH = "/tmp/dictate_trigger"

# GUI
root = tk.Tk()
root.title("Dictate test")
text = tk.Text(root)
text.pack()
text.focus_set()

typewrite_test = "typewrite_test"
result = ""
check_count = 0


def type_text():
    """Type the test text using pyautogui."""
    pyautogui.typewrite(typewrite_test)


def check_text():
    """Check for typed text, timeout after 10 seconds."""
    global result, check_count
    result = text.get("1.0", "end-1c").strip()
    check_count += 1

    # If we got text or checked for 10 seconds (100 * 100ms), close
    if result or check_count >= 100:
        text.delete("1.0", "end")  # Clear the text widget
        root.quit()
    else:
        root.after(100, check_text)


def check_result(expected, case_sensitive=True):
    """Check test result and print status."""
    global result
    passed = result == expected if case_sensitive else result.lower() == expected.lower()
    print(f"'{expected}' ", end="")
    if passed:
        print("pass")
    else:
        print(f"fail, got: '{result}'")
        sys.exit(1)
    return passed


root.after(600, check_text)  # Start checking after typing
# root.after(200, type_text)
root.after(200, lambda: pyautogui.typewrite(typewrite_test))
root.mainloop()
check_result(typewrite_test)

dictate_proc = subprocess.Popen(
    ["python3", "dictate.py", "--no-echo"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
)

for _ in range(30):
    if os.path.exists(FIFO_PATH):
        break
    time.sleep(0.1)
else:
    dictate_proc.terminate()
    sys.exit(1)


def play_audio(a):
    os.system(f"gtts-cli '{a}' | play -q -v 0.1 -t mp3 -")


def send_cmd(cmd):
    """Send command to FIFO."""
    fd = os.open(FIFO_PATH, os.O_WRONLY | os.O_NONBLOCK)
    os.write(fd, f"{cmd}\n".encode())
    os.close(fd)


sample = ""


def test_sequence():
    global sample
    sample = "hello"
    send_cmd("record")
    root.after(1000, lambda: play_audio(sample))
    root.after(3500, lambda: send_cmd("stop"))
    root.after(5000, check_text)


check_count = 0  # Reset for second test
time.sleep(1)
test_sequence()
root.mainloop()

dictate_proc.terminate()
dictate_proc.wait()

check_result(sample)
