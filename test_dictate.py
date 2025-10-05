#!/usr/bin/env python3
"""Test dictate.py speech recognition functionality - simplified version."""
import os
import subprocess
import sys
import time

import pyautogui
import yaml
from box import Box

from kbd_utils import for_typewrite, get_current_keyboard_layout, kbd_cfg

FIFO_PATH = "/tmp/dictate_test_trigger"
dictate_proc = None
cfg = None
errors = 0


def init():
    global dictate_proc, cfg
    dictate_proc = subprocess.Popen(
        ["python3", "dictate.py", "--no-echo", "--trigger", FIFO_PATH],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(30):
        if os.path.exists(FIFO_PATH):
            break
        time.sleep(0.1)
    else:
        dictate_proc.terminate()
        sys.exit(1)
    y = {}
    try:
        with open("dictate.yaml", "r", encoding="utf-8") as f:
            y = yaml.safe_load(f) or {}
    except Exception:
        pass
    cfg = Box(y, default_box=True)
    time.sleep(1)


def check_result(expected, result, case_sensitive=True):
    if result.strip().lower() == expected.lower():
        print("pass")
    else:
        print(f"Expected:  '{expected}' ", end="")
        print(f"fail, got: '{result}'")
        global errors
        errors += 1


def send_cmd(cmd):
    fd = os.open(FIFO_PATH, os.O_WRONLY | os.O_NONBLOCK)
    os.write(fd, f"{cmd}\n".encode())
    os.close(fd)


def play_audio(text, lang="en"):
    os.system(f"gtts-cli '{text}' -l {lang} | play -q -v 0.1 -t mp3 -")


def test_typewrite(sample):
    to_type = for_typewrite(sample, kl)
    pyautogui.typewrite(to_type + "\n")
    time.sleep(0.5)
    check_result(sample, input())


def test_dictate(sample, lang="en"):
    send_cmd("record")
    time.sleep(1)
    play_audio(sample, lang)
    time.sleep(2.5)
    send_cmd("stop")
    time.sleep(2)
    pyautogui.typewrite("\n")  # Press enter to submit
    check_result(sample, input())


init()
time.sleep(0.5)
kl = get_current_keyboard_layout()
print(f"Current keyboard layout: {kl}")

# Test typewrite with some sample text
test_samples = {
    "us": ["Hello", "Test"],
    "de": ["Hallo", "Straße"],
    "ru": ["Привет", "эхо"],
    "es": ["Hola", "niño"],
    "fr": ["Bonjour", "café"],
    "it": ["Ciao", "città"],
}

lang_code = kbd_cfg.layouts[kl].languages.tts or kl

# Test typewrite
if kl in test_samples:
    print("\nTesting typewrite:")
    for sample in test_samples[kl]:
        test_typewrite(sample)
else:
    print("\nTesting typewrite with default:")
    test_typewrite("Test")

# Test dictation with a simple phrase
print("\nTesting dictation:")
test_phrase = test_samples.get(kl, ["Hello"])[0]
test_dictate(test_phrase, lang_code)

dictate_proc.terminate()
dictate_proc.wait()

print(f"Errors: {errors}")
sys.exit(errors)
