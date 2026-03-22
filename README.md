# Mumble

Mumble is a desktop speech-to-text app built around the Qt redesign in `src/ui_redesign` and the shared speech layer in `src/shared`.

`run_modern_mumble.py` is the primary entrypoint. The older Tk applications in `src/launcher.py`, `src/launcher_enhanced.py`, `src/launcher_qt5.py`, `src/mumble_notes`, and `src/mumble_quick` remain in the repo as migration reference only.

## Current product shape

- Command palette and system tray app built with PyQt5
- Quick dictation mode for sending text into the active app with a deterministic `sounddevice` recording path
- Notes editor that now persists the working note between launches and can export timestamped note snapshots
- Shared adaptive speech backends in `src/shared`

## Quick start

### Prerequisites

- Python 3.10 or newer recommended
- Windows is the primary supported environment right now
- A working microphone

### Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

If microphone capture fails on Windows, verify that `sounddevice` installed cleanly and that the active input device is available to Python.

### Run

```bash
python run_modern_mumble.py
```

Or, after installing the package entrypoint:

```bash
mumble
```

When the app starts:

- `Ctrl+Shift+Space` opens the command palette
- `Ctrl+Alt+Space` starts/stops Quick mode dictation
- Use the tray icon to reopen Notes or exit the app

## Notes persistence

- Working notes are persisted in the app data directory used by Qt
- Exported notes are written to `~/Documents/Mumble Notes`
- Set `MUMBLE_DATA_DIR` to override the working-note storage root
- Set `MUMBLE_NOTES_EXPORT_DIR` to override the export directory

## Project layout

```text
run_modern_mumble.py     Primary launcher
src/ui_redesign/         Canonical Qt product UI
src/shared/              Shared speech, config, and logging modules
src/mumble_notes/        Legacy Tk reference
src/mumble_quick/        Legacy Tk reference
docs/installation.md     Detailed install notes
```

## Development

Run the focused migration checks:

```bash
pytest tests/test_mumble.py
```

The full historical pytest suite is not the release gate yet; some legacy tests still need cleanup as the Qt migration continues.

## Packaging

- `setup.py` is aligned to the Qt app entrypoint
- `Mumble.spec` targets `run_modern_mumble.py`

## Troubleshooting

- If the app fails to import Qt modules, verify `PyQt5` is installed in the active environment
- If quick dictation starts but no speech is captured, check microphone permissions and available speech backend dependencies
- If global hotkeys do not register, run the app in a normal desktop session with keyboard access enabled
