# Unified Launcher and Speech Recognition Improvements

## Summary
This PR adds a unified launcher for both Mumble applications and fixes speech recognition freezing issues. It also improves error handling, adds timeout mechanisms, and enhances the overall user experience.

## Changes
- Added a unified launcher UI for both Mumble applications
- Implemented exclusive application mode (only one app can run at a time)
- Fixed speech recognition freezing issues with timeout mechanisms
- Enhanced error handling and recovery for speech recognition
- Added VBS launcher and desktop shortcut utilities for Windows
- Updated documentation and refactor plan
- Added comprehensive logging throughout the application

## Testing
- [x] Tested launcher UI functionality
- [x] Verified exclusive application mode works correctly
- [x] Confirmed speech recognition works without freezing
- [x] Tested error handling and recovery
- [x] Verified VBS launcher and desktop shortcuts work correctly
- [x] Checked all logs for proper error reporting

## Screenshots
<!-- Add screenshots if applicable -->

## Related Issues
<!-- Link to any related issues -->

## Additional Notes
The speech recognition module now uses a timeout mechanism to prevent freezing during dictation. The timeout can be configured using the `MUMBLE_DICTATION_TIMEOUT` environment variable. 