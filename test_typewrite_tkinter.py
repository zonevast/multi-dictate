#!/usr/bin/env python3
"""Test pyautogui typewrite functionality with tkinter."""
import sys
import tkinter as tk
import pyautogui

root = tk.Tk()
text = tk.Text(root)
text.pack()
text.focus_set()

test_text = "Test123"
result = ""
check_count = 0

def type_text():
    """Type the test text using pyautogui."""
    pyautogui.typewrite(test_text)

def check_text():
    """Check for typed text, timeout after 10 seconds."""
    global result, check_count
    result = text.get("1.0", "end-1c")
    check_count += 1

    # If we got text or checked for 10 seconds (100 * 100ms), close
    if result or check_count >= 100:
        root.quit()
    else:
        # Check again in 100ms
        root.after(100, check_text)

root.after(200, type_text)
root.after(600, check_text)  # Start checking after typing
root.mainloop()

print(f"Typed: '{test_text}'")
print(f"Got:   '{result}'")
print("PASS" if result == test_text else "FAIL")
sys.exit(result != test_text)
