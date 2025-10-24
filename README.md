# Multi-Dictate

A voice dictation application for Linux that supports multiple languages.
The tool captures voice input, converts it to text using speech recognition,
and types it into any application while properly handling keyboard layout conversions.

## Features

- Multi-language voice-to-text dictation triggered via FIFO commands
- Multi-language support with automatic language detection based on keyboard layout
- Proper text input for non-QWERTY layouts (AZERTY, QWERTZ, etc.)
- Fast clipboard-based text insertion (much faster than typing)
- Text-to-speech echo of recognized text
- Visual status indicator during recording

## System Requirements

### Operating System
- Linux (tested on Fedora, Ubuntu, Debian)
- X11 or Wayland display server

## Installation

The installation script will:
- Install system dependencies
- Install Python dependencies
- Set up the application as a system service
- Enable automatic startup on boot

```bash
# Clone the repository (if not already done)
git clone https://github.com/makelinux/multi-dictate.git
cd multi-dictate

# Run the installation script
./install.sh
```

### Uninstallation

To completely remove the application:
```bash
./uninstall.sh
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

### After Installation

Once installed with `./install.sh`, the application is installed as a Python package and the service runs automatically:

1. **Check service status:**
   ```bash
   systemctl --user status dictate.service
   ```

2. **View service logs:**
   ```bash
   journalctl --user -u dictate.service -f
   ```

3. **Control the service:**
   ```bash
   # Stop the service
   systemctl --user stop dictate.service

   # Start the service
   systemctl --user start dictate.service

   # Restart the service
   systemctl --user restart dictate.service

   # Disable auto-start on boot
   systemctl --user disable dictate.service
   ```

### Using the Dictation Feature

1. Focus cursor on any input field or text editor
2. Use one of the following keybindings:
   - **Super+F11**: Start manual recording (press Super+F12 to stop)
   - **Super+Insert**: Toggle recording (press to talk)
   - **Ctrl+Shift+S**: Record until silence detected (automatic stop)
   - **Super+F10**: Toggle speech echo on/off
3. Speak clearly into your microphone
4. The recognized text will be typed at your cursor position

### Configuration

The application uses configuration files stored in:
- `~/.config/multi-dictate/dictate.yaml` - Main configuration
- `~/.config/multi-dictate/keyboard.yaml` - Keyboard layout mappings



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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
