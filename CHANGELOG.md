# Changelog

All notable changes to the Mumble applications will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2023-03-17

### Added
- New unified launcher UI for both Mumble applications
- System tray integration for easier access
- Exclusive application mode (only one app can run at a time)
- Improved error handling and recovery for speech recognition
- Timeout mechanisms to prevent freezing during dictation
- Health monitoring for running applications
- Desktop shortcut creation utility

### Fixed
- Fixed freezing issues during speech recognition/dictation
- Improved process management and termination
- Enhanced error logging and diagnostics
- Fixed UI visibility issues in Mumble Quick
- Resolved hotkey registration problems

### Changed
- Refactored speech recognition module for better stability
- Updated application launch mechanism to hide command prompts
- Improved user experience with status indicators
- Enhanced shutdown process with graceful termination

## [1.1.0] - 2023-03-10

### Added
- Separated codebase into Mumble Notes and Mumble Quick applications
- Shared modules for common functionality
- Configuration system with validation
- Settings dialogs for both applications
- Test suites for core components

### Changed
- Improved UI components for better user experience
- Enhanced speech recognition accuracy
- Optimized performance for large documents

### Fixed
- Various bug fixes and stability improvements
- Memory leaks in document handling
- UI responsiveness issues

## [1.0.0] - 2023-03-01

### Added
- Initial release of Mumble
- Basic note-taking functionality
- Speech-to-text capabilities
- Document management
- Simple formatting options

### Technical Features
- Comprehensive test suite
  - Unit tests for all components
  - Integration tests
  - Performance benchmarks
- Shared modules for speech recognition
- Configuration system
- Logging system
- Theme management

### Development Tools
- Added development environment setup
- Added continuous integration configuration
- Added code formatting (black)
- Added linting (flake8)
- Added test coverage reporting

### Documentation
- Added comprehensive README
- Added API documentation
- Added usage guides
- Added development guidelines
- Added contribution guidelines 