# Serenade WhisperAI

<div align="center">
  <h3>🎤 Voice-Controlled Coding Assistant Powered by OpenAI Whisper</h3>
  <p>A Python implementation of Serenade functionality with advanced speech recognition</p>
</div>

## 🌟 Features

### Core Functionality
- **Advanced Speech Recognition**: OpenAI Whisper (large-v3 model) for accurate transcription
- **Voice Activity Detection**: Real-time VAD for efficient audio processing
- **Multi-Language Support**: Code in Python, JavaScript, TypeScript, Java, C++, C#, Go, Rust
- **Intelligent Code Manipulation**: AST-based code editing and navigation
- **System Automation**: Full keyboard and mouse control
- **Cross-Platform**: Windows, macOS, Linux support
- **Offline Capable**: Run entirely on your local machine

### Voice Commands

#### Navigation
- "go to line [number]"
- "go to function [name]"
- "go to class [name]"
- "next/previous function"
- "scroll up/down"

#### Editing
- "add function [name]"
- "delete line/function/class"
- "change [target] to [value]"
- "rename [old name] to [new name]"
- "insert [code]"
- "copy/cut/paste"

#### Selection
- "select line [number]"
- "select function [name]"
- "select all"
- "select word/line/paragraph"

#### Custom Commands
- Create custom voice commands
- Macro recording and playback
- Context-aware command execution

## 🏗️ Architecture

```
serenade-whisperai/
├── src/
│   ├── core/              # Core application logic
│   │   ├── audio/         # Audio capture and processing
│   │   ├── speech/        # Whisper integration
│   │   ├── commands/      # Command parsing and execution
│   │   ├── ast/           # Abstract Syntax Tree handling
│   │   └── automation/    # System automation
│   ├── gui/               # PyQt6 user interface
│   ├── server/            # FastAPI backend server
│   ├── plugins/           # Editor plugins
│   └── utils/             # Utility functions
├── models/                # Whisper model storage
├── config/                # Configuration files
├── tests/                 # Unit and integration tests
└── build/                 # Build scripts for .exe
```

## 🚀 Installation

### Prerequisites
- Python 3.9 or higher
- CUDA-capable GPU (recommended for faster processing)
- Microphone
- 8GB+ RAM

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/prarthanadoshi7/serenade-whisperai.git
cd serenade-whisperai
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Download Whisper model** (first run will auto-download)
```bash
python src/core/speech/download_model.py
```

5. **Run the application**
```bash
python src/main.py
```

## 📦 Building .exe

### Using PyInstaller
```bash
pyinstaller build/serenade-whisperai.spec
```

### Using auto-py-to-exe (GUI)
```bash
auto-py-to-exe
# Load build/auto-py-to-exe-config.json
```

The built executable will be in `dist/serenade-whisperai.exe`

## ⚙️ Configuration

Edit `config/config.yml`:

```yaml
audio:
  sample_rate: 16000
  chunk_size: 1024
  vad_mode: 3  # 0-3, higher = more aggressive
  silence_duration: 1.5

whisper:
  model: large-v3  # tiny, base, small, medium, large, large-v3
  device: cuda  # cuda, cpu
  language: en
  fp16: true

commands:
  confidence_threshold: 0.7
  custom_commands_enabled: true
  
automation:
  typing_delay: 0.01
  mouse_speed: 1.0

gui:
  theme: dark
  always_on_top: false
  show_transcriptions: true
```

## 🎯 Usage

1. **Launch the application**
2. **Click the microphone button** or use hotkey (Ctrl+Shift+Space)
3. **Speak your command**
4. **Watch the magic happen!**

### Example Session

```
User: "create function calculate sum"
→ Creates: def calculate_sum():

User: "add parameter numbers"
→ Updates: def calculate_sum(numbers):

User: "insert return sum of numbers"
→ Updates: def calculate_sum(numbers):
              return sum(numbers)
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_speech_recognition.py
```

## 🔌 Editor Integration

Supported editors:
- VS Code (via extension)
- PyCharm / IntelliJ IDEA
- Sublime Text
- Vim / Neovim
- Emacs

## 📊 Performance

| Model | Size | Speed (GPU) | Accuracy |
|-------|------|-------------|----------|
| tiny | 39M | ~32x realtime | Good |
| base | 74M | ~16x realtime | Better |
| small | 244M | ~6x realtime | Great |
| medium | 769M | ~2x realtime | Excellent |
| large-v3 | 1550M | ~1x realtime | Best |

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition
- [Serenade](https://github.com/serenadeai/serenade) - Original inspiration
- [Tree-sitter](https://tree-sitter.github.io/) - Code parsing

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/prarthanadoshi7/serenade-whisperai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/prarthanadoshi7/serenade-whisperai/discussions)

## 🗺️ Roadmap

- [ ] Cloud sync for custom commands
- [ ] Multi-user collaboration
- [ ] Mobile app integration
- [ ] Browser extension
- [ ] AI-powered code suggestions
- [ ] Custom wake word support
- [ ] Voice profiles for multiple users

---

<div align="center">
  Made with ❤️ by developers who love coding hands-free
</div>
