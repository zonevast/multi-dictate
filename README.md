# Voice Dictation Tool for Linux

A voice dictation application for Linux that supports multiple keyboard layouts, including non-QWERTY layouts. The tool captures voice input, converts it to text using speech recognition, and types it into any application while properly handling keyboard layout conversions.

## Features

- Voice-to-text dictation triggered via FIFO commands
- Multi-language support with automatic language detection based on keyboard layout
- Proper text input for non-QWERTY layouts (AZERTY, QWERTZ, etc.)
- Text-to-speech echo of recognized text
- Visual status indicator during recording

## System Requirements

### Operating System
- Linux (tested on Fedora, Ubuntu, Debian)
- X11 or Wayland display server

### Quick install:
```bash
./install.sh
```

### Interfaces

- [Custom keyboard bindings](https://wiki.ubuntu.com/Keybindings)
- [`pasimple`](https://github.com/henrikschnor/pasimple) - PulseAudio interface
- [`webrtcvad`](https://github.com/wiseman/py-webrtcvad) - Voice Activity Detection
- [`speech_recognition`](https://github.com/Uberi/speech_recognition),  [Google Speech Recognition](https://github.com/Uberi/speech_recognition/blob/master/reference/library-reference.rst#recognizer_instancerecognize_googleaudio_data-audiodata-key-unionstr-none--none-language-str--en-us--pfilter-union0-1-show_all-bool--false---unionstr-dictstr-any)
- [`gtts`](https://gtts.readthedocs.io/) - Google Text-to-Speech for echo mode
- [`tkinter`](https://docs.python.org/3/library/tkinter.html) - for Visual status indicator
- [`pyautogui.typewrite`](https://pyautogui.readthedocs.io/en/latest/keyboard.html) - for final text output into keyboard buffer
- Remote desktop access

Optional packages:
- `python-Levenshtein` - For calibration mode only (`--calibrate`)
- [`vosk`](https://github.com/Uberi/speech_recognition/blob/master/reference/library-reference.rst#recognizer_instancerecognize_voskaudio_data-audiodata--verbose-bool--false---unionstr-dictstr-str) - For offline speech recognition

## Configuration

Configure custom keybindings to activate the dictation.

Check with
```bash
dconf dump /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/
```

### Language Settings

Edit `dictate.yaml` to configure:
- Recognition language preferences
- Text-to-speech settings
- Voice activity detection parameters


## Usage

1. Start the dictation service:
   ```bash
   ./dictate.py
   ```

Focus cursor on an input field or text editor.

Press activation key.

Allow remote interaction when requested.

## Troubleshooting

### Non-QWERTY Layout Issues

If text is typed incorrectly on non-QWERTY layouts:

1. Verify XKB tools are installed:
   ```bash
   which setxkbmap xkbcomp
   ```

2. Check layout detection:
   ```bash
   python -c "from kbd_utils import get_current_keyboard_layout; print(get_current_keyboard_layout())"
   ```

3. Test layout mapping:
   ```bash
   python test_dictate.py
   ```

4. On Wayland, you may see warnings about Xwayland - these can be safely ignored.

### Audio Issues

1. Check PulseAudio is running:
   ```bash
   pactl info
   ```

2. Test microphone:
   ```bash
   parecord test.wav
   paplay test.wav
   ```

## Development

### Testing

Run the built-in tests:
```bash
# Test keyboard layout conversions
python kbd_utils.py

# Test dictation
python test_dictate.py
```
