"""
Main Modern Mumble Application
Integrates the command palette, listening interface, and notes editor
"""

import sys
import os
import logging
import keyboard
from typing import Optional

from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QColor

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.adaptive_speech import create_adaptive_speech_recognizer
from shared.logging import setup_logging

from .command_palette import PaletteManager
from .listening_interface import ListeningManager
from .notes_editor import NotesManager
from .styles import COLORS


class HotkeyMonitor(QThread):
    """Thread for monitoring global hotkeys"""
    
    palette_requested = pyqtSignal()
    quick_mode_pressed = pyqtSignal()
    quick_mode_released = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.quick_mode_active = False
        
    def run(self):
        """Monitor for hotkeys"""
        self.running = True
        try:
            # Register palette hotkey (Ctrl+Shift+Space)
            keyboard.add_hotkey('ctrl+shift+space', self.on_palette_hotkey, suppress=True)
            
            # Register Quick mode hotkeys (Ctrl+Alt - press and hold)
            keyboard.add_hotkey('ctrl+alt', self.on_quick_mode_press, suppress=True, trigger_on_release=False)
            keyboard.add_hotkey('ctrl+alt', self.on_quick_mode_release, suppress=True, trigger_on_release=True)
            
            # Keep thread alive
            while self.running:
                keyboard.wait()
                
        except Exception as e:
            logging.error(f"Hotkey monitoring error: {e}")
    
    def on_palette_hotkey(self):
        """Handle palette hotkey press"""
        self.palette_requested.emit()
    
    def on_quick_mode_press(self):
        """Handle Quick mode key press (start of press-and-hold)"""
        if not self.quick_mode_active:
            self.quick_mode_active = True
            self.quick_mode_pressed.emit()
    
    def on_quick_mode_release(self):
        """Handle Quick mode key release (end of press-and-hold)"""
        if self.quick_mode_active:
            self.quick_mode_active = False
            self.quick_mode_released.emit()
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
        keyboard.unhook_all()


class MumbleApp(QObject):
    """Main Mumble application with modern UI"""
    
    def __init__(self):
        super().__init__()
        self.logger = setup_logging('mumble_modern')
        
        # State tracking
        self.quick_mode_waiting = False  # Track if Quick mode is waiting for activation
        
        # Initialize managers
        self.palette_manager = PaletteManager()
        self.listening_manager = ListeningManager()
        self.notes_manager = NotesManager()
        
        # Speech recognition
        self.recognizer = None
        self.setup_speech_recognition()
        
        # System tray
        self.tray_icon = None
        self.setup_system_tray()
        
        # Hotkey monitoring
        self.hotkey_monitor = None
        self.setup_hotkey_monitoring()
        
        # Connect signals
        self.connect_signals()
        
        # Set initial tray icon state
        self.update_tray_icon_state('idle')
        
        self.logger.info("Modern Mumble application initialized")
    
    def setup_speech_recognition(self):
        """Initialize speech recognition"""
        try:
            self.recognizer = create_adaptive_speech_recognizer()
            self.logger.info("Speech recognition initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize speech recognition: {e}")
    
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
        quick_info_action = QAction("Quick Mode: Hold Ctrl+Alt to use", self)
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
        self.hotkey_monitor.quick_mode_pressed.connect(self.start_quick_mode)
        self.hotkey_monitor.quick_mode_released.connect(self.stop_quick_mode)
        self.hotkey_monitor.start()
        self.logger.info("Hotkey monitoring started (Ctrl+Shift+Space for palette, Ctrl+Alt press-and-hold for Quick mode)")
    
    def connect_signals(self):
        """Connect all component signals"""
        # Note: Palette signals will be connected when the palette is first shown
        # since the palette is created lazily in PaletteManager.show_palette()
        
        # Listening manager signals - these components are created immediately
        if hasattr(self.listening_manager, 'interface') and self.listening_manager.interface:
            self.listening_manager.interface.listening_cancelled.connect(self.stop_quick_mode)
    
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
            self.logger.info("Notes editor opened")
        else:
            # If already open, just focus it
            if self.notes_manager.editor:
                self.notes_manager.editor.raise_()
                self.notes_manager.editor.activateWindow()
    
    def start_quick_mode(self):
        """Start Quick Mode (speech-to-text)"""
        if not self.listening_manager.is_active():
            self.listening_manager.start_listening()
            
            # Update tray icon to listening state
            self.update_tray_icon_state('listening')
            
            # Start speech recognition
            if self.recognizer:
                self.recognizer.start_listening(self.on_speech_recognized)
            
            self.logger.info("Quick mode started")
    
    def stop_quick_mode(self):
        """Stop Quick Mode"""
        if self.listening_manager.is_active():
            self.listening_manager.stop_listening()
            
            # Stop speech recognition
            if self.recognizer:
                self.recognizer.stop_listening()
            
            # Update tray icon back to idle state
            self.update_tray_icon_state('idle')
            
            self.logger.info("Quick mode stopped")
    
    def on_speech_recognized(self, text: str):
        """Handle recognized speech"""
        if text:
            self.logger.info(f"Speech recognized: {text}")
            
            # Stop listening
            self.stop_quick_mode()
            
            # Insert text into notes editor or active application
            if self.notes_manager.is_editor_open():
                self.notes_manager.append_text(text)
            else:
                # Insert into active application
                self.insert_text_to_active_app(text)
    
    def insert_text_to_active_app(self, text: str):
        """Insert text into the currently active application"""
        try:
            import pyperclip
            import pyautogui
            
            # Copy text to clipboard and paste
            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'v')
            self.logger.info("Text inserted into active application")
            
        except Exception as e:
            self.logger.error(f"Failed to insert text: {e}")
            # Fallback: open notes editor with the text
            self.notes_manager.open_editor(text)
    
    def on_tray_activated(self, reason):
        """Handle system tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_palette()
    
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
            self.tray_icon.setToolTip("Mumble - Quick Mode Waiting (Press Ctrl+Alt)")
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
                "Ctrl+Shift+Space for command palette • Hold Ctrl+Alt for Quick mode",
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