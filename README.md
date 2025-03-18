# Mumble

A suite of complementary applications for efficient note-taking and speech-to-text input, featuring Mumble Notes for comprehensive note management and Mumble Quick for instant dictation anywhere.

## Features

### Mumble Notes
- **Rich Text Editor** with comprehensive formatting options
- **Document Organization** with tags and categories
- **Speech-to-Text Integration** for efficient note-taking
- **Theme Customization** for comfortable viewing
- **Auto-save Functionality** to prevent data loss

### Mumble Quick
- **Minimal Floating Interface** with animated waveform
- **Global Hotkey Activation** (Ctrl+Alt+M or Ctrl+Shift+M)
- **Direct Text Insertion** into any active application
- **Visual Feedback** with smooth animations
- **Exclusive Mode** operation with Mumble Notes

## Quick Start

### Prerequisites
- Python 3.8 or higher ([Download](https://www.python.org/downloads/))
- Working microphone (built-in or external)
- Internet connection for speech recognition

### Installation

1. **Clone the Repository**:
   ```bash
   git clone <your-repo>
   cd <your-repo>
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Platform-Specific Setup**:
   - **Windows**: No additional setup needed
   - **macOS**: Grant accessibility permissions in System Preferences
   - **Linux**: Install portaudio:
     ```bash
     sudo apt-get install portaudio19-dev  # Debian/Ubuntu
     ```

### Running the Applications

1. **Using the Unified Launcher**:
   ```bash
   python src/launcher.py
   ```
   - Launch either Mumble Notes or Mumble Quick
   - Only one application can run at a time
   - Monitor application status through the launcher

2. **Windows Quick Launch** (No Command Prompt):
   - Double-click `launch_mumble.vbs` in the root directory
   - Or create a desktop shortcut using `create_shortcut.bat`

## Configuration

### Application Settings
Both applications use JSON configuration files:
- Mumble Notes: `src/mumble_notes/config/notes_config.json`
- Mumble Quick: `src/mumble_quick/config/quick_config.json`

### Environment Variables
- `MUMBLE_DICTATION_TIMEOUT`: Maximum dictation phrase duration in seconds (default: 10)

### Configurable Options

#### Mumble Notes
- Editor preferences
- Theme settings
- Document management options
- Speech recognition settings
- Auto-save interval

#### Mumble Quick
- Hotkey combinations
- UI appearance
- Speech recognition settings
- Animation settings

## Project Structure
```
/
├── launch_mumble.vbs       # VBS launcher (no command prompt)
├── create_shortcut.bat     # Desktop shortcut creator
└── src/
    ├── launcher.py         # Unified launcher
    ├── mumble_notes/       # Full-featured note-taking app
    ├── mumble_quick/       # Quick dictation tool
    ├── shared/             # Shared components
    ├── logs/               # Application logs
    └── tests/              # Test suites
```

## Development

### Running Tests
```bash
# Run all tests
pytest src/tests/

# Run specific test suite
pytest src/tests/test_integration.py
pytest src/tests/test_performance.py

# Run with coverage
pytest --cov=src tests/
```

### Performance Metrics
- Startup time
- Memory usage
- Speech recognition accuracy
- Document operations speed
- UI responsiveness

## Troubleshooting

### Common Issues

1. **Application Won't Start**
   - Verify Python 3.8+ installation: `python --version`
   - Check dependencies: `pip list`
   - Verify config files exist
   - Check logs in `src/logs/`

2. **Speech Recognition Issues**
   - Verify microphone connection and permissions
   - Check internet connectivity
   - Try shorter `MUMBLE_DICTATION_TIMEOUT` if freezing occurs
   - Review logs for error messages

3. **UI or Display Issues**
   - Check display scaling settings
   - Verify theme configuration
   - Ensure assets exist in `src/assets/`

4. **Launcher Issues**
   - Verify Python is in PATH
   - Use VBS launcher for Windows Store Python
   - Check logs for startup errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests for new functionality
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Speech recognition powered by [SpeechRecognition](https://pypi.org/project/SpeechRecognition/)
- UI components built with tkinter and ttkthemes
- Inspired by tools like Wispr Flow
