# Mumble Applications

A suite of two complementary applications for efficient note-taking and quick speech-to-text input.

## Quick Start

### Running the Applications

1. **Using the Unified Launcher**
   ```bash
   # Launch the Mumble Launcher
   python src/launcher.py
   ```
   - From the launcher, you can start either Mumble Notes or Mumble Quick
   - Only one application can run at a time
   - The launcher provides status indicators and easy application management

2. **Using the VBS Launcher** (Windows, no command prompt)
   - Double-click `launch_mumble.vbs` in the root directory
   - This launches the unified launcher without showing a command prompt

3. **Creating a Desktop Shortcut** (Windows)
   - Run `create_shortcut.bat` to create a desktop shortcut
   - The shortcut will launch the Mumble Launcher without showing a command prompt

### First Time Setup
1. Install Python 3.8 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Applications

### Mumble Notes
A full-featured note-taking application with rich text editing capabilities and document management.

**Key Features:**
- Rich text editor with formatting options
- Document organization and management
- Speech-to-text integration
- Theme customization
- Auto-save functionality

### Mumble Quick
A lightweight speech-to-text tool for quick text input anywhere in your system.

**Key Features:**
- Minimal floating pill-bar interface
- Global hotkey activation (Ctrl+Alt+M or Ctrl+Shift+M)
- Direct text insertion into active applications
- Smooth animations and visual feedback

## Configuration

Both applications use JSON configuration files located in their respective directories:

- Mumble Notes: `src/mumble_notes/config/notes_config.json`
- Mumble Quick: `src/mumble_quick/config/quick_config.json`

### Environment Variables

The following environment variables can be used to customize behavior:
- `MUMBLE_DICTATION_TIMEOUT`: Maximum duration for a single dictation phrase in seconds (default: 10)

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

## Development

### Project Structure
```
/
├── launch_mumble.vbs       # VBS launcher (no command prompt)
├── create_shortcut.bat     # Desktop shortcut creator
└── src/
    ├── launcher.py         # Unified launcher for both applications
    ├── mumble_notes/
    │   ├── app.py
    │   ├── config/
    │   ├── ui/
    │   └── utils/
    ├── mumble_quick/
    │   ├── app.py
    │   ├── config/
    │   ├── ui/
    │   └── utils/
    ├── shared/
    │   ├── speech_recognition.py
    │   └── logging.py
    ├── logs/               # Application logs directory
    └── tests/
        ├── test_integration.py
        └── test_performance.py
```

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

### Performance Benchmarks
```bash
python src/tests/test_performance.py
```

Key metrics monitored:
- Startup time
- Memory usage
- Speech recognition performance
- Document operations speed
- UI responsiveness

## Troubleshooting

### Common Issues

1. **Application Won't Start**
   - Verify Python 3.8+ is installed: `python --version`
   - Check all dependencies are installed: `pip list`
   - Ensure config files exist in correct locations
   - Check logs in `src/logs/` directory

2. **Speech Recognition Issues**
   - Verify microphone is connected and working
   - Check microphone permissions in system settings
   - Ensure internet connection for cloud-based recognition
   - If dictation freezes, try setting a shorter `MUMBLE_DICTATION_TIMEOUT` value
   - Check the logs for specific error messages

3. **UI or Display Issues**
   - Verify display scaling settings
   - Check theme configuration
   - Ensure all assets are present in `src/assets/`

4. **Launcher Issues**
   - If the launcher doesn't appear, check if Python is in your PATH
   - For Windows Store Python, use the VBS launcher or desktop shortcut
   - If applications don't start from the launcher, check the logs

### Error Messages

Common error messages and their solutions:
- "Could not find app.py": Verify installation directory structure
- "ModuleNotFoundError": Run `pip install -r requirements.txt`
- "Permission Error": Run with appropriate permissions
- "Config Error": Check config file format and permissions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Speech recognition powered by [SpeechRecognition](https://pypi.org/project/SpeechRecognition/)
- UI components built with tkinter and ttkthemes 