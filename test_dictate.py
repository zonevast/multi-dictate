#!/usr/bin/env python3
"""Test dictate.py speech recognition functionality - simplified version."""
import os
import subprocess
import sys
import time

import pyautogui

FIFO_PATH = "/tmp/dictate_trigger"
dictate_proc = None


def init():
    global dictate_proc
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
    time.sleep(1)


def check_result(expected, result, case_sensitive=True):
    if result.strip().lower() == expected.lower():
        print("pass")
    else:
        print(f"Expected:  '{expected}' ", end="")
        print(f"fail, got: '{result}'")
        sys.exit(1)


def send_cmd(cmd):
    fd = os.open(FIFO_PATH, os.O_WRONLY | os.O_NONBLOCK)
    os.write(fd, f"{cmd}\n".encode())
    os.close(fd)


def play_audio(text):
    os.system(f"gtts-cli '{text}' | play -q -v 0.1 -t mp3 -")


def test_dictate(sample):
    send_cmd("record")
    time.sleep(1)
    play_audio(sample)
    time.sleep(2.5)
    send_cmd("stop")
    time.sleep(2)
    pyautogui.typewrite("\n")  # Press enter to submit
    check_result(sample, input())


time.sleep(0.5)
TYPEWRITE_TEST = "typewrite_test"
pyautogui.typewrite(TYPEWRITE_TEST + "\n")
check_result(TYPEWRITE_TEST, input())
init()
test_dictate("English")
dictate_proc.terminate()
dictate_proc.wait()
