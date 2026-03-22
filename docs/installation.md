# Installation

This project now ships around the Qt application launched by `run_modern_mumble.py`.

## Supported path

- Primary environment: Windows desktop
- Primary UI: `src/ui_redesign`
- Shared runtime layer: `src/shared`
- Legacy Tk applications are not the recommended install or launch path

## Setup

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
pip install -e .
```

The modern Qt app uses `sounddevice` for Quick dictation, so a working Python microphone device is more important than PyAudio.

## Launch

Start the product with:

```bash
python run_modern_mumble.py
```

Installed entrypoint:

```bash
mumble
```

Expected behavior:

- The app stays resident in the system tray
- `Ctrl+Shift+Space` opens the command palette
- `Ctrl+Alt+Space` starts or stops Quick mode dictation
- Notes open in the Qt notes editor and restore the last working note automatically

## Storage locations

- Working note state: Qt app data directory
- Exported note snapshots: `~/Documents/Mumble Notes`

Optional overrides:

- `MUMBLE_DATA_DIR`: overrides the working-state storage root
- `MUMBLE_NOTES_EXPORT_DIR`: overrides the export directory
- `MUMBLE_DICTATION_TIMEOUT`: maximum phrase duration in seconds for compatible recognizers

## Verification

Run the focused migration baseline:

```bash
pytest tests/test_mumble.py
```

The broader legacy pytest suite is still under cleanup and should not be treated as a release signal yet.
