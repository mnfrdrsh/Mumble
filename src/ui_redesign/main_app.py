"""
Main Modern Mumble Application
Integrates the command palette, listening interface, and notes editor
"""

import sys
import logging
import time
import keyboard

from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QColor

from shared.logging import setup_logging

from .command_palette import PaletteManager
from .listening_interface import ListeningManager
from .notes_editor import NotesManager
from .quick_dictation import QuickDictationController
from .styles import COLORS


class HotkeyMonitor(QThread):
    """Thread for monitoring global hotkeys"""
    
    palette_requested = pyqtSignal()
    quick_mode_toggled = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.running = False
        self._hotkey_handles = []
        
    def run(self):
        """Monitor for hotkeys"""
        self.running = True
        try:
            # Register palette hotkey (Ctrl+Shift+Space)
            self._hotkey_handles.append(
                keyboard.add_hotkey('ctrl+shift+space', self.on_palette_hotkey, suppress=True)
            )
            
            # Register Quick mode hotkey (Ctrl+Alt+Space)
            self._hotkey_handles.append(
                keyboard.add_hotkey('ctrl+alt+space', self.on_quick_mode_toggle, suppress=True)
            )
            
            # Keep thread alive without blocking shutdown on a pending keyboard event.
            while self.running:
                self.msleep(100)
                
        except Exception as e:
            logging.error(f"Hotkey monitoring error: {e}")
        finally:
            self._remove_hotkeys()
    
    def on_palette_hotkey(self):
        """Handle palette hotkey press"""
        self.palette_requested.emit()
    
    def on_quick_mode_toggle(self):
        """Handle Quick mode toggle hotkey."""
        self.quick_mode_toggled.emit()
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
        self._remove_hotkeys()

    def _remove_hotkeys(self):
        """Remove only the hotkeys registered by this monitor."""
        while self._hotkey_handles:
            handle = self._hotkey_handles.pop()
            try:
                keyboard.remove_hotkey(handle)
            except (KeyError, ValueError):
                continue


class MumbleApp(QObject):
    """Main Mumble application with modern UI"""
    
    speech_recognized = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.logger = setup_logging('mumble_modern')
        
        # State tracking
        self.quick_mode_waiting = False  # Track if Quick mode is waiting for activation
        self._quick_mode_session = 0
        self._active_quick_mode_session = None
        
        # Initialize managers
        self.palette_manager = PaletteManager()
        self.listening_manager = ListeningManager()
        self.notes_manager = NotesManager()
        
        # Quick dictation
        self.recognizer = None
        self.setup_quick_dictation()
        
        # System tray
        self.tray_icon = None
        self.setup_system_tray()
        
        # Hotkey monitoring
        self.hotkey_monitor = None
        self.setup_hotkey_monitoring()
        
        # Connect signals
        self.connect_signals()
        self.speech_recognized.connect(self.handle_recognized_text)
        
        # Set initial tray icon state
        self.update_tray_icon_state('idle')
        
        self.logger.info("Modern Mumble application initialized")
    
    def setup_quick_dictation(self):
        """Initialize the deterministic quick dictation controller."""
        try:
            self.recognizer = QuickDictationController()
            self.recognizer.transcription_failed.connect(self.on_quick_mode_transcription_failed)
            self.recognizer.state_changed.connect(self.on_quick_mode_state_changed)
            self.logger.info(
                f"Quick dictation initialized ({self.recognizer.backend_name} backend)"
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize quick dictation: {e}")
    
    def setup_system_tray(self):
        """Setup system tray icon and menu"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self.logger.warning("System tray not available")
            return
        
        # Create tray icon
        self.tray_icon = QSystemTrayIcon()
        
        # Create a simple colored icon
        icon_pixmap = QPixmap(16, 16)
        icon_pixmap.fill(QColor(COLORS['accent_blue']))
        self.tray_icon.setIcon(QIcon(icon_pixmap))
        
        # Create context menu
        tray_menu = QMenu()
        
        # Show Command Palette
        palette_action = QAction("Show Command Palette", self)
        palette_action.triggered.connect(self.show_palette)
        tray_menu.addAction(palette_action)
        
        tray_menu.addSeparator()
        
        # Quick actions
        notes_action = QAction("Open Notes", self)
        notes_action.triggered.connect(self.open_notes)
        tray_menu.addAction(notes_action)
        
        # Info action for Quick mode
        quick_info_action = QAction("Quick Mode: Ctrl+Alt+Space to start or stop", self)
        quick_info_action.setEnabled(False)  # Make it non-clickable info
        tray_menu.addAction(quick_info_action)
        
        tray_menu.addSeparator()
        
        # Exit
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.exit_application)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Double-click to show palette
        self.tray_icon.activated.connect(self.on_tray_activated)
        
        self.logger.info("System tray initialized")
    
    def setup_hotkey_monitoring(self):
        """Setup global hotkey monitoring"""
        self.hotkey_monitor = HotkeyMonitor()
        self.hotkey_monitor.palette_requested.connect(self.show_palette)
        self.hotkey_monitor.quick_mode_toggled.connect(self.toggle_quick_mode)
        self.hotkey_monitor.start()
        self.logger.info("Hotkey monitoring started (Ctrl+Shift+Space for palette, Ctrl+Alt+Space to toggle Quick mode)")
    
    def connect_signals(self):
        """Connect all component signals"""
        # Note: Palette signals will be connected when the palette is first shown
        # since the palette is created lazily in PaletteManager.show_palette()
        self.listening_manager.listening_cancelled.connect(self.cancel_quick_mode)
    
    def show_palette(self):
        """Show the command palette"""
        self.palette_manager.show_palette()
        
        # Connect palette signals if this is the first time the palette was created
        if self.palette_manager.palette and not hasattr(self, '_palette_signals_connected'):
            self.palette_manager.palette.launch_notes.connect(self.open_notes)
            self.palette_manager.palette.launch_quick.connect(self.start_quick_mode)
            self._palette_signals_connected = True
        
        self.logger.info("Command palette shown")
    
    def open_notes(self):
        """Open the notes editor"""
        if not self.notes_manager.is_editor_open():
            self.notes_manager.open_editor()
            self._connect_notes_editor_signals()
            self.logger.info("Notes editor opened")
        else:
            # If already open, just focus it
            if self.notes_manager.editor:
                self._connect_notes_editor_signals()
                self.notes_manager.editor.raise_()
                self.notes_manager.editor.activateWindow()

    def _connect_notes_editor_signals(self):
        """Connect per-editor signals for the active notes window."""
        editor = self.notes_manager.editor
        if not editor or getattr(editor, "_launcher_signal_connected", False):
            return

        editor.launcher_requested.connect(self.show_palette)
        editor._launcher_signal_connected = True

    def toggle_quick_mode(self):
        """Toggle Quick mode on or off."""
        if self.listening_manager.is_active():
            self.finish_quick_mode()
        else:
            self.start_quick_mode()
    
    def start_quick_mode(self):
        """Start Quick Mode (speech-to-text)"""
        if self.listening_manager.is_active():
            return

        if not self.recognizer or not self.recognizer.is_available:
            self.logger.warning("Quick mode requested without an available dictation backend")
            self.show_notification(
                "Quick Dictation Unavailable",
                "Install the sounddevice package to use Quick mode.",
            )
            return

        if self.recognizer.is_busy:
            self.logger.info("Quick mode requested while dictation is still busy")
            return

        self._quick_mode_session += 1
        session_id = self._quick_mode_session
        self._active_quick_mode_session = session_id

        self.listening_manager.start_listening()

        # Update tray icon to listening state
        self.update_tray_icon_state('listening')

        try:
            self.recognizer.start_listening(
                lambda text, session_id=session_id: self.on_speech_recognized(text, session_id)
            )
        except Exception as e:
            self.logger.error(f"Failed to start quick dictation: {e}")
            self.cancel_quick_mode()
            return

        self.logger.info("Quick mode started")

    def finish_quick_mode(self):
        """Stop recording and start transcribing the captured audio."""
        was_active = self.listening_manager.is_active()
        recognizer_was_listening = bool(self.recognizer and self.recognizer.is_listening)

        if was_active:
            self.listening_manager.stop_listening()

        if recognizer_was_listening:
            self.recognizer.stop_listening()

        if was_active or recognizer_was_listening:
            self.update_tray_icon_state('waiting')
            self.logger.info("Quick mode recording stopped; waiting for transcription")

    def stop_quick_mode(self):
        """Compatibility wrapper for finishing the current quick dictation session."""
        self.finish_quick_mode()

    def cancel_quick_mode(self):
        """Cancel the current quick dictation session without transcribing."""
        self._active_quick_mode_session = None
        was_active = self.listening_manager.is_active()
        recognizer_was_listening = bool(self.recognizer and self.recognizer.is_listening)

        if was_active:
            self.listening_manager.stop_listening()

        if recognizer_was_listening and hasattr(self.recognizer, "cancel_listening"):
            self.recognizer.cancel_listening()

        if was_active or recognizer_was_listening:
            self.update_tray_icon_state('idle')
            self.logger.info("Quick mode cancelled")

    def on_speech_recognized(self, text: str, session_id=None):
        """Handle recognized speech"""
        if not text:
            return

        if session_id is not None and session_id != self._active_quick_mode_session:
            self.logger.info("Ignoring stale Quick Mode transcription from an inactive session")
            return

        # Invalidate the session before handing the text back to the UI thread so
        # duplicate backend callbacks cannot insert the same result twice.
        if session_id is not None:
            self._active_quick_mode_session = None

        self.speech_recognized.emit(text)

    def handle_recognized_text(self, text: str):
        """Handle recognized speech on the Qt main thread."""
        self.logger.info(f"Speech recognized: {text}")

        if self.listening_manager.is_active():
            self.listening_manager.stop_listening()
        self._active_quick_mode_session = None
        self.update_tray_icon_state('idle')

        # Insert text into notes editor or active application
        if self.notes_manager.is_editor_open():
            self.notes_manager.append_text(text)
            self._connect_notes_editor_signals()
        else:
            # Insert into active application
            self.insert_text_to_active_app(text)
    
    def insert_text_to_active_app(self, text: str):
        """Insert text into the currently active application"""
        try:
            previous_clipboard = self._get_clipboard_text()
            self._set_clipboard_text(text)

            # Give the OS clipboard a moment to propagate before pasting.
            time.sleep(0.05)
            self._paste_clipboard_to_active_app()
            self._schedule_clipboard_restore(previous_clipboard)
            self.logger.info("Text inserted into active application")
            
        except Exception as e:
            self.logger.error(f"Failed to insert text: {e}")
            # Fallback: open notes editor with the text
            self.notes_manager.open_editor(text)
            self._connect_notes_editor_signals()

    def _get_clipboard_text(self) -> str:
        """Read the current clipboard contents."""
        import pyperclip

        return pyperclip.paste()

    def _set_clipboard_text(self, text: str):
        """Write text to the clipboard."""
        import pyperclip

        pyperclip.copy(text)

    def _paste_clipboard_to_active_app(self):
        """Send the OS paste hotkey to the active application."""
        import pyautogui

        pyautogui.hotkey('ctrl', 'v')

    def _schedule_clipboard_restore(self, previous_clipboard: str):
        """Restore the previous clipboard contents after the paste completes."""
        QTimer.singleShot(
            150,
            lambda previous_clipboard=previous_clipboard: self._restore_clipboard_text(previous_clipboard),
        )

    def _restore_clipboard_text(self, previous_clipboard: str):
        """Best-effort clipboard restoration after active-app paste."""
        try:
            self._set_clipboard_text(previous_clipboard)
        except Exception as e:
            self.logger.warning(f"Failed to restore clipboard after paste: {e}")
    
    def on_tray_activated(self, reason):
        """Handle system tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_palette()

    def on_quick_mode_transcription_failed(self, message: str):
        """Handle a failed quick dictation transcription."""
        self.logger.warning(f"Quick mode transcription failed: {message}")
        self._active_quick_mode_session = None
        self.update_tray_icon_state('idle')
        self.show_notification("Quick Dictation", message)

    def on_quick_mode_state_changed(self, state: str):
        """Keep tray state aligned with the dictation controller."""
        if state == "recording":
            self.update_tray_icon_state('listening')
        elif state == "transcribing":
            self.update_tray_icon_state('waiting')
        elif state == "idle" and not self.listening_manager.is_active():
            self.update_tray_icon_state('idle')

    def show_notification(self, title: str, message: str, duration_ms: int = 3000):
        """Best-effort desktop notification through the tray icon."""
        if self.tray_icon:
            self.tray_icon.showMessage(title, message, QSystemTrayIcon.Information, duration_ms)
    
    def exit_application(self):
        """Exit the application"""
        self.logger.info("Exiting application")
        
        # Cleanup
        if self.hotkey_monitor:
            self.hotkey_monitor.stop()
            self.hotkey_monitor.wait()
        
        self.palette_manager.cleanup()
        self.listening_manager.cleanup()
        self.notes_manager.cleanup()
        
        if self.tray_icon:
            self.tray_icon.hide()
        
        QApplication.quit()
    
    def update_tray_icon_state(self, state: str):
        """Update tray icon state"""
        if not self.tray_icon:
            return
        
        # Create a colored icon based on the state
        icon_pixmap = QPixmap(16, 16)
        if state == 'idle':
            icon_pixmap.fill(QColor(COLORS['accent_blue']))
        elif state == 'waiting':
            icon_pixmap.fill(QColor(COLORS['accent_green']))
        elif state == 'listening':
            icon_pixmap.fill(QColor(COLORS['accent_red']))
        
        self.tray_icon.setIcon(QIcon(icon_pixmap))
        
        # Update tooltip
        if state == 'idle':
            self.tray_icon.setToolTip("Mumble - Ready")
        elif state == 'waiting':
            self.tray_icon.setToolTip("Mumble - Transcribing quick dictation...")
        elif state == 'listening':
            self.tray_icon.setToolTip("Mumble - Listening...")


def main():
    """Main entry point"""
    # Create QApplication
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running when windows are closed
    app.setStyle('Fusion')
    
    # Set application properties
    app.setApplicationName("Mumble")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Mumble")
    
    # Dark theme
    app.setStyleSheet(f"""
        QApplication {{
            background-color: {COLORS['background']};
        }}
    """)
    
    # Create and run the main application
    try:
        mumble_app = MumbleApp()
        
        # Show initial welcome message
        if mumble_app.tray_icon:
            mumble_app.tray_icon.showMessage(
                "Mumble Started",
                "Ctrl+Shift+Space for command palette | Ctrl+Alt+Space for Quick mode",
                QSystemTrayIcon.Information,
                4000
            )
        
        sys.exit(app.exec_())
        
    except KeyboardInterrupt:
        logging.info("Received keyboard interrupt")
    except Exception as e:
        logging.error(f"Application error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 
