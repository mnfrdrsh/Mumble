# Mumble Architecture

## Overview

Mumble is a simple speech-to-text application that allows users to transcribe their speech into text using their microphone. The application is built using Python with a Tkinter-based GUI and leverages Google's Speech Recognition service through the SpeechRecognition library.

The application offers two modes of operation:
1. **Standard Mode**: A GUI-based application with a two-column layout for managing transcriptions
2. **Hotkey Mode**: A background application that allows inserting transcribed text into any active application using hotkeys

![System Context Diagram](https://via.placeholder.com/800x400?text=Mumble+System+Context+Diagram)

### Key Architectural Principles

- **Simplicity**: Keep the application simple and focused on core functionality
- **Responsiveness**: Ensure the UI remains responsive during speech recognition
- **Reliability**: Handle errors gracefully and provide clear feedback to users
- **Usability**: Provide an intuitive interface for managing transcriptions
- **Flexibility**: Support different usage patterns through multiple operation modes

## Component Architecture

### Main Components

1. **User Interface (UI)**: 
   - Built with Tkinter
   - Two-column layout with transcription area and saved pages list
   - Provides controls for starting/stopping recording and managing pages
   - Displays transcribed text in real-time

2. **Speech Recognition Engine**:
   - Uses the SpeechRecognition library
   - Connects to Google's Speech Recognition service
   - Processes audio input from the microphone

3. **Temporary Page Storage System**:
   - Manages in-memory storage of transcribed pages
   - Provides functionality to create, view, and delete pages
   - Pages are stored only during the application session

4. **File Management**:
   - Handles saving transcribed text to files
   - Manages file dialogs and error handling

5. **Hotkey System**:
   - Monitors keyboard input for specific key combinations
   - Manages recording state based on hotkey presses
   - Inserts transcribed text into the active application

### Data Flow

#### Standard Mode
1. User speaks into the microphone
2. Audio is captured and processed by the SpeechRecognition library
3. Audio is sent to Google's Speech Recognition service
4. Transcribed text is returned and displayed in the UI
5. User can save the transcribed text as a temporary page
6. User can select, view, and manage temporary pages
7. User can save selected pages to permanent files

#### Hotkey Mode
1. User presses and holds the start hotkey (Ctrl+Space or Command+Space)
2. Audio recording begins
3. User releases the hotkey and continues speaking
4. User presses the stop key (Space) to end recording
5. Audio is processed and transcribed
6. Transcribed text is inserted into the active application

## Technical Decisions

### GUI Framework: Tkinter

**Decision**: Use Tkinter for the GUI.

**Rationale**: 
- Comes bundled with Python, no additional installation required
- Simple and lightweight
- Cross-platform compatibility

**Alternatives Considered**:
- PyQt/PySide: More feature-rich but requires additional dependencies
- wxPython: Good cross-platform support but more complex

### Speech Recognition: SpeechRecognition + Google API

**Decision**: Use the SpeechRecognition library with Google's Speech Recognition service.

**Rationale**:
- Easy to use Python interface
- Good accuracy with Google's service
- Free for basic usage

**Alternatives Considered**:
- CMU Sphinx: Offline but less accurate
- Whisper: More accurate but requires more resources

### Temporary Page Storage: In-Memory

**Decision**: Use in-memory storage for temporary pages.

**Rationale**:
- Simple implementation
- Fast access and manipulation
- No need for database setup
- Pages are intended to be temporary by design

**Alternatives Considered**:
- SQLite: More persistent but adds complexity
- File-based storage: More durable but slower and more complex

### Hotkey System: Keyboard + PyAutoGUI

**Decision**: Use the keyboard and PyAutoGUI libraries for hotkey functionality.

**Rationale**:
- keyboard library provides cross-platform hotkey detection
- PyAutoGUI enables text insertion into any application
- Simple implementation without requiring system-level integration

**Alternatives Considered**:
- System-specific APIs: More powerful but less portable
- Custom keyboard hooks: More complex to implement and maintain

## Data Model

The application has the following data model:
- Audio input (transient)
- Transcribed text (stored in memory during session)
- Temporary pages (stored in memory during session)
  - Each page has a timestamp, preview, and content
- Saved text files (persistent storage)

## Non-Functional Requirements

### Security
- No sensitive data is stored by the application
- Audio data is only sent to Google's servers during transcription
- Temporary pages are cleared when the application is closed

### Performance
- The application should start quickly
- Transcription should occur with minimal delay
- UI should remain responsive during transcription
- Page management operations should be instantaneous
- Hotkey detection should be responsive with minimal latency

### Reliability
- The application should handle network errors gracefully
- Clear error messages should be provided to the user
- Confirmation dialogs for destructive actions
- Hotkey mode should provide clear feedback on its state

### Compatibility
- The application should work on Windows, macOS, and Linux
- Platform-specific adaptations for hotkeys and sound notifications

## Implementation Notes

### Technology Stack
- Python 3.8+
- Tkinter for GUI
- SpeechRecognition library
- PyAudio for microphone access
- keyboard for hotkey detection
- PyAutoGUI for text insertion
- pyperclip for clipboard operations

### Development Environment
- Any standard Python development environment
- Requires a microphone for testing

## Future Considerations

### Known Limitations
- Requires internet connection for transcription
- Limited to languages supported by Google's Speech Recognition
- Temporary pages are lost when the application is closed
- No advanced text editing features
- Hotkey mode may require elevated privileges on some platforms
- Some hotkey combinations may conflict with system shortcuts

### Evolution Path
1. Add support for offline transcription
2. Implement multiple language support
3. Add text editing features
4. Create a more advanced UI with themes
5. Add speech recognition customization options
6. Implement optional persistent storage for pages
7. Add cloud synchronization for pages
8. Enhance hotkey functionality with customizable shortcuts
9. Add system tray integration for hotkey mode 