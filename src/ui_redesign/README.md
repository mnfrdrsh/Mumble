# Mumble UI Redesign

A modern, command palette-style interface for the Mumble speech-to-text application, featuring beautiful glassmorphism design, smooth animations, and intuitive user experience.

## 🎨 Features

### Modern Command Palette
- **Glassmorphism Design**: Semi-transparent cards with blur effects
- **Dark Theme**: Professional dark interface with blue/purple accents
- **Smooth Animations**: Fade and scale transitions for all UI elements
- **Keyboard Navigation**: Full keyboard support with ESC to close
- **Search Filtering**: Type to filter available actions
- **Status Awareness**: Shows which applications are currently running

### Animated Listening Interface
- **Beautiful Waveform**: Real-time animated bars with gradient colors
- **Responsive Design**: Bars animate based on different frequency ranges
- **Smooth Transitions**: Elegant fade in/out animations
- **Interactive**: Click outside or press ESC to cancel

### Modern Notes Editor
- **Card-based Design**: Clean, floating interface
- **Rich Text Support**: Full-featured text editing
- **Auto-save Indicators**: Visual feedback for unsaved changes
- **Clipboard Integration**: One-click copy functionality
- **Keyboard Shortcuts**: Standard shortcuts (Ctrl+S, Ctrl+W, ESC)
- **Drag Support**: Move the editor window by dragging

## 🚀 Quick Start

### Running the Demo
```bash
# Simple demo launcher
python run_demo.py

# Or run directly
python -m src.ui_redesign.demo
```

### Running the Full Application
```bash
# Modern Mumble launcher
python run_modern_mumble.py

# Or run directly
python -m src.ui_redesign.main_app
```

### Testing Individual Components
```bash
# Command Palette only
python -m src.ui_redesign.command_palette

# Listening Interface only
python -m src.ui_redesign.listening_interface

# Notes Editor only
python -m src.ui_redesign.notes_editor
```

## 🎯 Usage

### Global Hotkey
- **Ctrl+Shift+Space**: Open the command palette from anywhere

### Command Palette Actions
- **Launch Mumble Notes**: Opens the full notes editor
- **Launch Mumble Quick**: Starts speech-to-text mode
- **Type to Search**: Filter actions by typing
- **Enter**: Execute the first visible action
- **ESC**: Close the palette

### Speech-to-Text (Quick Mode)
1. Launch from command palette or system tray
2. Beautiful listening interface appears
3. Speak your text
4. Text is automatically inserted into active application or notes editor

### Notes Editor
- **Save**: Ctrl+S or click Save button
- **Copy**: Click Copy button to copy all text to clipboard
- **Close**: ESC, Ctrl+W, or click Close button
- **Auto-save indicator**: Button shows "*" when there are unsaved changes

## 🏗️ Architecture

### Component Structure
```
src/ui_redesign/
├── __init__.py              # Package initialization
├── styles.py                # Centralized styling system
├── command_palette.py       # Main launcher interface
├── listening_interface.py   # Speech recognition UI
├── notes_editor.py         # Notes editing interface
├── main_app.py             # Integrated application
└── demo.py                 # Demo and testing
```

### Key Classes

#### `CommandPalette`
- Main launcher dialog with search and action buttons
- Handles keyboard navigation and filtering
- Manages application state and process launching

#### `ListeningInterface`
- Animated waveform visualization
- Handles speech recognition feedback
- Smooth show/hide animations

#### `NotesEditor`
- Full-featured text editor with modern styling
- File operations (save, copy)
- Keyboard shortcuts and drag support

#### `MumbleApp`
- Main application coordinator
- System tray integration
- Global hotkey monitoring
- Speech recognition integration

## 🎨 Design System

### Color Palette
- **Background**: `#1a1a1a` (Dark)
- **Card Background**: `rgba(40, 40, 45, 0.95)` (Semi-transparent)
- **Accent Blue**: `#2196f3`
- **Accent Purple**: `#9c27b0`
- **Text Primary**: `#ffffff`
- **Text Secondary**: `#b8b8b8`

### Typography
- **Font Family**: Inter, Segoe UI, Roboto, sans-serif
- **Sizes**: Small (11px), Medium (13px), Large (16px), Header (20px), Title (24px)
- **Weights**: Normal (400), Medium (500), Bold (600)

### Animations
- **Fade Duration**: 200-300ms
- **Scale Duration**: 250-400ms
- **Easing**: OutCubic, OutBack for bouncy effects
- **Waveform**: 20 FPS smooth animation

## 🔧 Technical Details

### Dependencies
- **PyQt5**: Modern Qt-based GUI framework
- **pyperclip**: Clipboard operations
- **keyboard**: Global hotkey monitoring
- **Existing Mumble modules**: Speech recognition, logging

### Performance Optimizations
- **Lazy Loading**: UI components created only when needed
- **Efficient Animations**: Hardware-accelerated Qt animations
- **Memory Management**: Proper cleanup of resources
- **Event-driven**: Minimal CPU usage when idle

### Cross-platform Compatibility
- **Windows**: Full support with system tray
- **macOS**: Compatible (may need minor adjustments)
- **Linux**: Compatible (requires proper permissions for global hotkeys)

## 🐛 Known Issues

### Qt Styling Limitations
- `backdrop-filter` and `box-shadow` CSS properties not supported by Qt
- Fallback to solid backgrounds and Qt's built-in shadow effects
- Font warnings on systems with unusual font installations

### Windows-specific
- `UpdateLayeredWindowIndirect` warnings are cosmetic and don't affect functionality
- Global hotkeys may require administrator privileges in some cases

## 🔮 Future Enhancements

### Planned Features
- **Theme Customization**: Light/dark mode toggle
- **Plugin System**: Extensible action system
- **Voice Commands**: "Open notes", "Start listening" voice triggers
- **Recent Files**: Quick access to recent notes
- **Settings Panel**: Configurable hotkeys and preferences

### Performance Improvements
- **Native Blur Effects**: Platform-specific blur implementations
- **Reduced Memory Usage**: More efficient animation systems
- **Faster Startup**: Optimized initialization

## 🤝 Contributing

### Development Setup
1. Install dependencies: `pip install PyQt5 pyperclip keyboard`
2. Run tests: `python -m src.ui_redesign.demo`
3. Make changes to components in `src/ui_redesign/`
4. Test individual components before integration

### Code Style
- Follow existing patterns in the codebase
- Use type hints where appropriate
- Document new features and changes
- Maintain the centralized styling system

## 📝 License

This UI redesign follows the same license as the main Mumble project.

---

**Built with ❤️ for a better speech-to-text experience** 