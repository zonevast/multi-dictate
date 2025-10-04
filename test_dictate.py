#!/usr/bin/env python3
"""Test dictate.py speech recognition functionality - simplified version."""
import os
import subprocess
import sys
import time

import pyautogui
import yaml
from box import Box

from kbd_utils import build_layout_mappings, get_current_keyboard_layout

FIFO_PATH = "/tmp/dictate_trigger"
dictate_proc = None
cfg = None
layout_mappings = None


def init():
    global dictate_proc, cfg, layout_mappings
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
    y = {}
    try:
        with open("dictate.yaml", "r", encoding="utf-8") as f:
            y = yaml.safe_load(f) or {}
    except Exception:
        pass
    cfg = Box(y, default_box=True)
    layout_mappings = build_layout_mappings(cfg.layouts)
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


def test_typewrite(sample):
    mapping = layout_mappings.get(kl)
    to_type = "".join(mapping.get(c, c) for c in sample) if mapping else sample
    pyautogui.typewrite(to_type + "\n")
    time.sleep(0.5)
    check_result(sample, input())


def test_dictate(sample):
    send_cmd("record")
    time.sleep(1)
    play_audio(sample)
    time.sleep(2.5)
    send_cmd("stop")
    time.sleep(2)
    pyautogui.typewrite("\n")  # Press enter to submit
    check_result(sample, input())


init()
time.sleep(0.5)
kl = get_current_keyboard_layout()
if kl not in ['us', 'de']:
    print(kl)
    for r in cfg.layouts[kl]["keys"].split():
        test_typewrite(r)
test_dictate("English")
dictate_proc.terminate()
dictate_proc.wait()
