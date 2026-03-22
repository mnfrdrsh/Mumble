#!/usr/bin/env python3
"""
Focused regression tests for the modern Mumble migration path.
"""

import os
import sys
import logging
import types
import inspect
import builtins
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

for import_root in (PROJECT_ROOT, SRC_ROOT):
    import_root_str = str(import_root)
    if import_root_str not in sys.path:
        sys.path.insert(0, import_root_str)

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication

from shared.adaptive_speech import create_adaptive_speech_recognizer
from shared.pyaudio_recognizer import PyAudioRecognizer
from shared.cloud_speech import WindowsSpeechRecognizer
import modern_mumble_launcher
import run_modern_mumble
from ui_redesign import command_palette
from ui_redesign import listening_interface
from ui_redesign import main_app
from ui_redesign.quick_dictation import QuickDictationController
from ui_redesign.notes_editor import NotesEditor, NotesStorage
from ui_redesign.styles import LAUNCHER_STYLE, LISTENING_STYLE, NOTES_STYLE


def get_app():
    """Return a QApplication instance for Qt object tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def build_headless_app(monkeypatch, recognizer_factory):
    """Create a MumbleApp instance without tray or hotkey side effects."""

    class DummyPaletteManager:
        def cleanup(self):
            return None

        def show_palette(self):
            return None

    class DummyNotesManager:
        def __init__(self):
            self.opened_text = []

        def cleanup(self):
            return None

        def is_editor_open(self):
            return False

        def open_editor(self, text=""):
            self.opened_text.append(text)

    class DummyListeningManager(QObject):
        listening_cancelled = pyqtSignal()

        def __init__(self):
            super().__init__()
            self._active = False

        def cleanup(self):
            return None

        def is_active(self):
            return self._active

        def start_listening(self):
            self._active = True

        def stop_listening(self):
            self._active = False

    monkeypatch.setattr(main_app, "PaletteManager", DummyPaletteManager)
    monkeypatch.setattr(main_app, "NotesManager", DummyNotesManager)
    monkeypatch.setattr(main_app, "ListeningManager", DummyListeningManager)
    monkeypatch.setattr(main_app, "setup_logging", lambda name: logging.getLogger(name))
    monkeypatch.setattr(
        main_app.MumbleApp,
        "setup_system_tray",
        lambda self: setattr(self, "tray_icon", None),
    )
    monkeypatch.setattr(
        main_app.MumbleApp,
        "setup_hotkey_monitoring",
        lambda self: setattr(self, "hotkey_monitor", None),
    )
    monkeypatch.setattr(
        main_app.MumbleApp,
        "setup_quick_dictation",
        lambda self: setattr(self, "recognizer", recognizer_factory()),
    )

    return main_app.MumbleApp()


def test_shared_speech_factory_imports():
    """The shared speech factory should be importable from the canonical package path."""
    assert callable(create_adaptive_speech_recognizer)
    assert "sys.path.append" not in inspect.getsource(main_app)


def test_modern_launcher_delegates_to_qt_entrypoint(monkeypatch):
    """The canonical launcher should call the Qt app entrypoint."""
    calls = []
    dummy_module = types.SimpleNamespace(main=lambda: calls.append("launched"))

    monkeypatch.setitem(sys.modules, "ui_redesign.main_app", dummy_module)

    assert run_modern_mumble.main() == 0
    assert calls == ["launched"]


def test_packaged_launcher_delegates_to_qt_entrypoint(monkeypatch):
    """The installed console entrypoint should call the Qt app entrypoint."""
    calls = []
    dummy_module = types.SimpleNamespace(main=lambda: calls.append("launched"))

    monkeypatch.setitem(sys.modules, "ui_redesign.main_app", dummy_module)

    assert modern_mumble_launcher.main() == 0
    assert calls == ["launched"]


def test_palette_manager_stays_in_process(monkeypatch):
    """The command palette manager should not wire legacy subprocess launch handlers."""

    class DummySignal:
        def __init__(self):
            self.connected = []

        def connect(self, callback):
            self.connected.append(callback)

    class DummyPalette:
        def __init__(self):
            self.launch_notes = DummySignal()
            self.launch_quick = DummySignal()
            self.palette_closed = DummySignal()
            self.status_updates = []
            self.show_calls = 0

        def update_app_status(self, notes_running, quick_running):
            self.status_updates.append((notes_running, quick_running))

        def show_animated(self):
            self.show_calls += 1

        def close(self):
            return None

    monkeypatch.setattr(command_palette, "CommandPalette", DummyPalette)

    manager = command_palette.PaletteManager()
    manager.show_palette()

    assert manager.palette.launch_notes.connected == []
    assert manager.palette.launch_quick.connected == []
    assert len(manager.palette.palette_closed.connected) == 1
    assert manager.palette.status_updates == [(False, False)]
    assert manager.palette.show_calls == 1


def test_palette_uses_explicit_hide_flag():
    """The launcher should not carry a stale hide callback across open/close cycles."""
    source = inspect.getsource(command_palette.CommandPalette)

    assert "_hide_on_fade = False" in source
    assert "def on_fade_finished" in source
    assert "if self._hide_on_fade:" in source


def test_qt_styles_avoid_unsupported_web_properties():
    """The canonical Qt stylesheets should avoid unsupported browser-only properties."""
    combined_styles = "\n".join([LAUNCHER_STYLE, LISTENING_STYLE, NOTES_STYLE])

    assert "backdrop-filter" not in combined_styles
    assert "box-shadow" not in combined_styles
    assert "line-height" not in combined_styles


def test_notes_editor_exposes_launcher_button_signal():
    """The notes editor should expose a direct path back to the launcher."""
    source = inspect.getsource(NotesEditor)

    assert "launcher_requested = pyqtSignal()" in source
    assert "self.launcher_requested.emit()" in source


def test_listening_interface_avoids_windows_layered_window_setup():
    """The listening overlay should avoid the Windows-hostile layered window setup."""
    source = inspect.getsource(listening_interface.ListeningInterface)

    assert "WA_TranslucentBackground" not in source
    assert "scale_animation" not in source
    assert "setFixedSize(self.sizeHint())" in source


def test_quick_dictation_controller_uses_sounddevice_backend():
    """The modern Qt quick dictation path should be deterministic."""
    source = inspect.getsource(QuickDictationController)

    assert "sounddevice" in source
    assert "recognize_google" in source
    assert "RawInputStream" in source


def test_pyaudio_recognizer_fails_fast_without_pyaudio(monkeypatch):
    """Missing PyAudio should be detected before quick mode starts listening."""
    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "pyaudio":
            raise ImportError("missing test dependency")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    try:
        PyAudioRecognizer()
    except ImportError as exc:
        assert "PyAudio is not installed" in str(exc)
    else:
        raise AssertionError("PyAudioRecognizer should fail fast when pyaudio is unavailable")


def test_windows_speech_script_suppresses_event_registration_output():
    """Windows speech should use a one-phrase recognition loop instead of event-job output."""
    source = inspect.getsource(WindowsSpeechRecognizer.start_listening)

    assert "Register-ObjectEvent" not in source
    assert "$recognizer.Recognize()" in source
    assert "Write-Output $result.Text" in source


def test_windows_speech_loop_uses_local_process_for_cleanup():
    """Windows speech cleanup should not dereference a cleared self._process handle."""
    source = inspect.getsource(WindowsSpeechRecognizer._run_powershell_recognition_loop)

    assert "process = subprocess.Popen" in source
    assert "if process.stderr:" in source


def test_quick_mode_toggle_starts_and_stops(monkeypatch):
    """Quick mode should now be a single toggle flow instead of press-and-hold."""
    get_app()

    class DummyRecognizer:
        def __init__(self):
            self.is_listening = False
            self.is_available = True
            self.is_busy = False
            self.is_transcribing = False
            self.backend_name = "dummy"
            self.start_calls = 0
            self.stop_calls = 0
            self.cancel_calls = 0

        def start_listening(self, callback):
            self.is_listening = True
            self.is_busy = True
            self.start_calls += 1
            self.callback = callback

        def stop_listening(self):
            self.is_listening = False
            self.is_busy = False
            self.stop_calls += 1

        def cancel_listening(self):
            self.is_listening = False
            self.is_busy = False
            self.cancel_calls += 1

    app = build_headless_app(monkeypatch, DummyRecognizer)

    app.toggle_quick_mode()
    assert app.recognizer.start_calls == 1
    assert app.listening_manager.is_active() is True

    app.toggle_quick_mode()
    assert app.recognizer.stop_calls == 1
    assert app.listening_manager.is_active() is False


def test_hotkey_monitor_uses_toggle_shortcut():
    """The canonical quick-mode shortcut should be a single toggle hotkey."""
    source = inspect.getsource(main_app.HotkeyMonitor.run)

    assert "ctrl+alt+space" in source
    assert "trigger_on_release" not in source


def test_notes_storage_persists_working_note_and_exports(tmp_path):
    """The Qt notes storage should preserve the working note and export snapshots."""
    storage = NotesStorage(
        base_dir=tmp_path / "state",
        export_dir=tmp_path / "exports",
    )

    saved_path = storage.save_working_note("persistent note")
    export_path = storage.export_note("persistent note")

    assert saved_path.exists()
    assert storage.load_working_note() == "persistent note"
    assert export_path.exists()
    assert export_path.read_text(encoding="utf-8") == "persistent note"


def test_notes_export_avoids_filename_collisions(tmp_path):
    """Multiple exports in the same second should not overwrite each other."""
    storage = NotesStorage(
        base_dir=tmp_path / "state",
        export_dir=tmp_path / "exports",
    )
    first_export = storage.export_note("first")
    second_export = storage.export_note("second")

    assert first_export != second_export
    assert first_export.read_text(encoding="utf-8") == "first"
    assert second_export.read_text(encoding="utf-8") == "second"


def test_quick_mode_cancel_signal_stops_recognizer(monkeypatch):
    """Cancelling the listening UI should stop the active recognizer."""
    get_app()

    class DummyRecognizer:
        def __init__(self):
            self.is_listening = True
            self.is_available = True
            self.is_busy = True
            self.is_transcribing = False
            self.backend_name = "dummy"
            self.cancel_calls = 0

        def cancel_listening(self):
            self.is_listening = False
            self.is_busy = False
            self.cancel_calls += 1

    app = build_headless_app(monkeypatch, DummyRecognizer)
    app.listening_manager.listening_cancelled.emit()

    assert app.recognizer.cancel_calls == 1


def test_cancelled_quick_mode_callback_is_ignored(monkeypatch):
    """Callbacks from a cancelled quick-mode session should not insert text."""
    get_app()

    class DummyRecognizer:
        def __init__(self):
            self.is_listening = False
            self.is_available = True
            self.is_busy = False
            self.is_transcribing = False
            self.backend_name = "dummy"
            self.callback = None
            self.stop_calls = 0

        def start_listening(self, callback):
            self.is_listening = True
            self.is_busy = True
            self.callback = callback

        def stop_listening(self):
            self.is_listening = False
            self.is_busy = False
            self.stop_calls += 1

        def cancel_listening(self):
            self.is_listening = False
            self.is_busy = False

    app = build_headless_app(monkeypatch, DummyRecognizer)

    inserted_text = []
    monkeypatch.setattr(
        main_app.MumbleApp,
        "insert_text_to_active_app",
        lambda self, text: inserted_text.append(text),
    )

    app.start_quick_mode()
    assert app.recognizer.callback is not None

    app.cancel_quick_mode()
    app.recognizer.callback("late transcription")

    assert inserted_text == []


def test_insert_text_restores_clipboard_after_paste(monkeypatch):
    """Active-app paste should restore the previous clipboard contents."""
    get_app()

    class DummyRecognizer:
        def __init__(self):
            self.is_listening = False
            self.is_available = True
            self.is_busy = False
            self.is_transcribing = False
            self.backend_name = "dummy"

    app = build_headless_app(monkeypatch, DummyRecognizer)

    clipboard_events = []

    monkeypatch.setattr(main_app.QTimer, "singleShot", lambda delay, callback: callback())
    monkeypatch.setattr(main_app.time, "sleep", lambda seconds: None)
    monkeypatch.setattr(
        main_app.MumbleApp,
        "_get_clipboard_text",
        lambda self: "previous clipboard",
    )
    monkeypatch.setattr(
        main_app.MumbleApp,
        "_set_clipboard_text",
        lambda self, text: clipboard_events.append(("set", text)),
    )
    monkeypatch.setattr(
        main_app.MumbleApp,
        "_paste_clipboard_to_active_app",
        lambda self: clipboard_events.append(("paste", None)),
    )

    app.insert_text_to_active_app("new dictation")

    assert clipboard_events == [
        ("set", "new dictation"),
        ("paste", None),
        ("set", "previous clipboard"),
    ]
