# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

### Development and Testing
```bash
# Run from source directory (development mode)
./run_dictate.py

# Run tests
pytest
make check

# Run specific test file
pytest test_dictate_unit.py

# Run tests with coverage
make test-coverage

# Linting
make lint
./lint.sh

# Clean temporary files
make clean
```

### Installation and Service Management
```bash
# Install as system service
./install.sh

# Uninstall completely
./uninstall.sh

# Service control (after installation)
systemctl --user status dictate.service
systemctl --user start dictate.service
systemctl --user stop dictate.service
systemctl --user restart dictate.service

# View service logs
journalctl --user -u dictate.service -f
```

### Manual Testing
```bash
# Test keyboard layout detection
python -c "from kbd_utils import get_current_keyboard_layout; print(get_current_keyboard_layout())"

# Test dictation functionality
python test_dictate.py

# Test audio recording/playback
parecord test.wav
paplay test.wav
```

## Architecture Overview

### Core Components

**Main Application (`multi_dictate/dictate.py`)**
- Central orchestrator handling audio recording, speech recognition, and text output
- Manages keyboard shortcuts via FIFO interface
- Integrates with multiple AI processors for enhanced functionality
- Handles text-to-speech feedback and visual status indicators

**Keyboard Utilities (`multi_dictate/kbd_utils.py`)**
- Critical for non-QWERTY keyboard layout support (AZERTY, QWERTZ, etc.)
- Detects current keyboard layout using XKB tools
- Provides character mapping for proper text output across layouts
- Manages custom keybinding configuration via dconf/GSettings

**AI Processing Pipeline**
The application includes multiple AI processors for enhanced dictation capabilities:
- `smart_ai_router.py` - Intelligently routes between available AI APIs
- `openai_processor.py` - OpenAI GPT integration
- `gemini_processor.py` - Google Gemini integration
- `problem_solver_processor.py` - Specialized problem-solving AI
- `rag_enhanced_processor.py` - Retrieval-Augmented Generation for context-aware processing
- `simple_rag_processor.py` - Basic RAG implementation

**Vector Database and Knowledge Base**
- `chroma_vector_db.py` / `enhanced_chroma_db.py` - Vector storage implementations
- `knowledge_base.py` - Manages domain-specific knowledge
- `vector_store.py` - Abstract interface for vector operations

### Audio and Speech Processing

**Audio Input Chain:**
1. PulseAudio interface via `pasimple` library
2. Voice Activity Detection using `webrtcvad`
3. Audio processing with `pydub`
4. Speech recognition via `speech_recognition` library (Google Speech API)

**Output Methods:**
- Primary: `pyautogui.typewrite` for direct keyboard input
- Secondary: Text-to-speech feedback via `gTTS`
- Visual: `tkinter` status indicator

### Configuration System

**Configuration Locations:**
- Main config: `~/.config/multi-dictate/dictate.yaml`
- Keyboard layouts: `~/.config/multi-dictate/keyboard.yaml` or package `keyboard.yaml`
- AI success tracking: `~/.config/multi-dictate/ai_success.json`

**Key Configuration Areas:**
- Custom keybindings (Super+F9 through F12, Ctrl+Shift+S)
- Recognition language preferences
- Text-to-speech settings
- Voice activity detection parameters
- AI processor selection and API keys

### Integration Points

**System Integration:**
- Runs as user systemd service after installation
- Integrates with GNOME custom keybindings system
- Supports both X11 and Wayland (with Xwayland fallback)

**Remote Desktop Support:**
- Firefox extension integration in `firefox-remote-control/`
- Native messaging host for browser control

### Dependencies

**Core Dependencies:**
- `pyautogui` - Keyboard automation
- `speech_recognition` - Speech-to-text conversion
- `webrtcvad` - Voice activity detection
- `pasimple` - PulseAudio interface
- `pydub` - Audio processing
- `gtts` - Text-to-speech
- `yaml` + `box` - Configuration management

**Optional Dependencies:**
- `vosk` - Offline speech recognition
- `python-Levenshtein` - Calibration mode
- Various AI SDKs (openai, google-generativeai) for enhanced features

### Testing Strategy

**Unit Tests:** `test_dictate_unit.py` - Core functionality tests
**Integration Tests:** `wrapping_test_dictate.py` - End-to-end testing
**Manual Tests:** `test_dictate.py` - Interactive testing with keyboard layout validation

### Key Design Patterns

**Modular Processor Architecture:** AI processors are pluggable and can be selected via the smart router based on availability and success history.

**Graceful Degradation:** The application provides stubs for missing dependencies (pyautogui, pasimple) to enable testing in headless environments.

**Multi-Language Support:** Automatic language detection based on keyboard layout, with proper character mapping for international keyboards.