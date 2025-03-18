# Mumble Application Refactoring Plan

## Overview
The Mumble application will be split into two distinct and independently runnable applications:

1. **Mumble Notes** (evolved from main.py)
   - Focus on note-taking and organization
   - Full GUI interface
   - Document management capabilities
   - Rich text formatting
   - Standalone configuration

2. **Mumble Quick** (evolved from mumble_hotkey.py)
   - Focus on quick speech-to-text input
   - Minimalist UI: pill-shaped floating bar (120px × 20px)
   - Activation via hotkey (Ctrl+Alt+M or Ctrl+Shift+M) with animation
   - Direct text insertion into active applications
   - Standalone configuration

## Tasks

### Phase 1: Core Separation ✓

1. [x] Create new directory structure:
   ```
   src/
   ├── launcher.py
   ├── mumble_notes/
   │   ├── __init__.py
   │   ├── app.py
   │   ├── config/
   │   │   └── notes_config.ini
   │   ├── ui/
   │   └── utils/
   ├── mumble_quick/
   │   ├── __init__.py
   │   ├── app.py
   │   ├── config/
   │   │   └── quick_config.ini
   │   ├── ui/
   │   │   ├── pill_bar.py
   │   │   └── animations.py
   │   └── utils/
   ├── shared/
   │   ├── __init__.py
   │   ├── speech_recognition.py
   │   └── logging.py
   └── logs/
   ```

2. [x] Extract shared functionality:
   - Speech recognition core
   - Logging utilities
   - Basic UI utilities

3. [x] Separate configurations:
   - Create independent config files for each application
   - Move existing settings to appropriate config files
   - Implement config validation for each app

### Phase 2: Mumble Quick Enhancement ✓

1. [x] Implement new UI components:
   - Create pill-shaped floating bar (120px × 20px)
   - Design smooth activation animation
   - Implement hotkey trigger (Ctrl+Alt+M or Ctrl+Shift+M)
   - Add visual feedback for recording state
   - Ensure bar stays on top of other windows
   - Add close controls

2. [x] Enhance hotkey functionality:
   - Configure hotkeys as primary triggers
   - Add visual feedback when hotkey is pressed
   - Implement smooth show/hide animations

3. [x] Improve error handling and stability:
   - Add comprehensive logging
   - Implement timeout mechanisms for speech recognition
   - Add graceful error recovery

### Phase 3: Mumble Notes Enhancement ✓

1. [x] Refactor main.py into modular components:
   - Document management system
   - Rich text editor
   - Page organization
   - Export/import capabilities

2. [x] Add new features:
   - Auto-save functionality
   - Document templates
   - Tags and categories
   - Search functionality
   - Export to various formats (PDF, MD, DOC)

### Phase 4: Polish and Optimization ✓

1. [x] Performance optimization:
   - Minimize memory usage through efficient configuration handling
   - Optimize startup time with lazy loading
   - Reduce CPU usage during idle with event-driven updates

2. [x] UI/UX improvements:
   - Smooth animations in both applications
   - Consistent styling with theme support
   - Comprehensive error handling and user feedback
   - Settings dialogs with live preview

3. [x] Launcher and deployment:
   - Create unified launcher for both applications
   - Implement exclusive application mode
   - Add process monitoring and management
   - Create deployment scripts for easy installation

### Phase 5: Quality Assurance (In Progress)

1. [✓] Create test suites:
   - [x] Configuration handler tests
   - [x] Settings dialog tests for both applications
   - [x] Speech recognition module tests
   - [x] UI component tests (Mumble Quick pill bar)
   - [x] UI component tests (Mumble Notes editor)
   - [x] UI component tests (Mumble Notes document manager)
   - [ ] Integration tests
   - [ ] Performance benchmarks

2. [ ] Documentation:
   - [x] Installation guides
   - [ ] User manuals
   - [ ] API documentation
   - [ ] Developer guides

## Next Steps (Prioritized)

1. [x] Implement Speech Recognition Tests
   - [x] Test speech-to-text conversion accuracy
   - [x] Test ambient noise handling
   - [x] Test language switching
   - [x] Test error recovery scenarios
   - [x] Test timeout mechanisms

2. [x] Create UI Component Tests
   - [x] Test pill bar animations and positioning
   - [x] Test pill bar waveform visualization
   - [x] Test pill bar dragging and interactions
   - [x] Test rich text editor functionality
   - [x] Test document manager operations
   - [x] Test theme switching and customization

3. [x] Implement Launcher and Deployment
   - [x] Create unified launcher UI
   - [x] Implement exclusive application mode
   - [x] Add process monitoring and health checks
   - [x] Create VBS launcher for Windows
   - [x] Add desktop shortcut creation utility

4. Develop Integration Tests
   - [ ] Test end-to-end workflows
   - [ ] Test inter-component communication
   - [ ] Test file operations and persistence
   - [ ] Test multi-window interactions

5. Create Performance Test Suite
   - [ ] Measure startup time
   - [ ] Test memory usage under load
   - [ ] Evaluate UI responsiveness
   - [ ] Profile speech recognition performance

6. Write Documentation
   - [x] Installation and setup guides
   - [ ] User manuals with screenshots
   - [ ] API documentation for developers
   - [ ] Configuration reference guide

## Timeline Update
- Phase 1-4: ✓ Completed (11 days)
- Phase 5: In progress (1-2 days remaining)
  - Test implementation: ~85% complete
  - Documentation: ~25% complete

## Recent Achievements
1. Created unified launcher UI with exclusive application mode
2. Implemented robust speech recognition with timeout mechanisms
3. Added comprehensive error handling and recovery
4. Created VBS launcher and desktop shortcut utilities
5. Completed extensive test suites for:
   - Configuration handling
   - Settings dialogs
   - Speech recognition module
   - Mumble Quick pill bar UI
   - Mumble Notes rich text editor
   - Mumble Notes document manager
6. Updated installation guides and README

## Implementation Notes
- Launcher provides a clean, professional interface for both applications
- Speech recognition module now has timeout mechanisms to prevent freezing
- Error handling is comprehensive with detailed logging
- Windows deployment is simplified with VBS launcher and desktop shortcuts
- Configuration system is fully tested and robust
- Settings dialogs provide excellent user experience with live preview
- Ready to proceed with integration tests

## Dependencies

### Shared Dependencies
- Python 3.8+
- speech_recognition
- pillow
- pytest (for testing)

### Mumble Quick Dependencies
- keyboard
- pyperclip
- pyautogui
- tkinter (for minimal UI)

### Mumble Notes Dependencies
- tkinter
- ttkthemes (for enhanced UI)

## Next Tasks
1. Create integration test suite
2. Implement performance benchmarks
3. Complete user documentation
4. Create release packages 