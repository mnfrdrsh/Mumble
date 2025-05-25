"""
Command Palette Launcher - Modern UI for Mumble
Inspired by modern command palette interfaces with glassmorphism design
"""

import sys
import os
import subprocess
import logging
from typing import Optional

from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QFrame, 
    QLabel, QLineEdit, QPushButton, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QFont, QPixmap, QIcon, QKeySequence

from .styles import LAUNCHER_STYLE, COLORS, apply_shadow_effect, create_icon


class ActionButton(QPushButton):
    """Custom action button with icon, text, and hotkey display"""
    
    def __init__(self, icon_text: str, main_text: str, hotkey: str = "", enabled: bool = True):
        super().__init__()
        self.setObjectName("action_button")
        self.setEnabled(enabled)
        
        # Create layout
        layout = QHBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)
        
        # Icon
        icon_label = create_icon(icon_text, size=20, color=COLORS['text_secondary'])
        layout.addWidget(icon_label)
        
        # Main text
        text_label = QLabel(main_text)
        text_label.setStyleSheet(f"""
            color: {COLORS['text_primary'] if enabled else COLORS['text_muted']};
            font-weight: 500;
        """)
        layout.addWidget(text_label)
        
        # Spacer
        layout.addStretch()
        
        # Hotkey (if provided)
        if hotkey:
            hotkey_label = QLabel(hotkey)
            hotkey_label.setObjectName("hotkey")
            layout.addWidget(hotkey_label)
        
        self.setLayout(layout)
        self.setFixedHeight(56)


class CommandPalette(QDialog):
    """Main command palette interface"""
    
    # Signals
    launch_notes = pyqtSignal()
    launch_quick = pyqtSignal()
    palette_closed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger('mumble.ui.palette')
        
        # State tracking
        self.notes_running = False
        self.quick_running = False
        
        self.init_ui()
        self.setup_animations()
        self.setup_shortcuts()
        
    def init_ui(self):
        """Initialize the user interface"""
        # Window configuration
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        
        # Apply styling
        self.setStyleSheet(LAUNCHER_STYLE)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Card container
        self.card = QFrame()
        self.card.setObjectName("card")
        self.card.setFixedSize(480, 420)
        apply_shadow_effect(self.card)
        
        # Card layout
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(32, 32, 32, 32)
        card_layout.setSpacing(24)
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)
        
        # App icon
        app_icon = create_icon("📝", size=24, color=COLORS['accent_blue'])
        header_layout.addWidget(app_icon)
        
        # Title
        title = QLabel("Mumble Launcher")
        title.setObjectName("header")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        card_layout.addLayout(header_layout)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search")
        self.search_input.setPlaceholderText("launch mumble...")
        self.search_input.textChanged.connect(self.filter_actions)
        card_layout.addWidget(self.search_input)
        
        # Action buttons container
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(8)
        
        # Notes action
        self.notes_action = ActionButton(
            "📄", "Launch Mumble Notes", "⌘N", enabled=not self.notes_running
        )
        self.notes_action.clicked.connect(self.on_launch_notes)
        actions_layout.addWidget(self.notes_action)
        
        # Quick action
        self.quick_action = ActionButton(
            "⚡", "Launch Mumble Quick", "Hold Ctrl+Alt", enabled=not self.quick_running
        )
        self.quick_action.clicked.connect(self.on_launch_quick)
        actions_layout.addWidget(self.quick_action)
        
        card_layout.addLayout(actions_layout)
        
        # Warning message
        warning_layout = QHBoxLayout()
        warning_icon = create_icon("⚠", size=16, color=COLORS['warning'])
        warning_layout.addWidget(warning_icon)
        
        warning_text = QLabel("Only one application can run at time")
        warning_text.setObjectName("warning")
        warning_layout.addWidget(warning_text)
        warning_layout.addStretch()
        
        card_layout.addLayout(warning_layout)
        
        # Add card to main layout
        main_layout.addWidget(self.card, alignment=Qt.AlignCenter)
        self.setLayout(main_layout)
        
        # Set initial focus
        self.search_input.setFocus()
        
    def setup_animations(self):
        """Setup entrance and exit animations"""
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self.scale_animation = QPropertyAnimation(self.card, b"geometry")
        self.scale_animation.setDuration(250)
        self.scale_animation.setEasingCurve(QEasingCurve.OutBack)
        
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # ESC to close
        self.escape_shortcut = QKeySequence("Esc")
        
        # Arrow key navigation
        # TODO: Implement arrow key navigation between action buttons
        
    def show_animated(self):
        """Show the palette with animation"""
        # Center on screen
        screen = QApplication.desktop().screenGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
        
        # Initial state for animations
        self.setWindowOpacity(0)
        self.show()
        
        # Animate fade in
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.start()
        
        # Animate scale in
        final_rect = self.card.geometry()
        start_rect = QRect(
            final_rect.x() + 20,
            final_rect.y() + 20,
            final_rect.width() - 40,
            final_rect.height() - 40
        )
        
        self.scale_animation.setStartValue(start_rect)
        self.scale_animation.setEndValue(final_rect)
        self.scale_animation.start()
        
    def hide_animated(self):
        """Hide the palette with animation"""
        self.fade_animation.setStartValue(1)
        self.fade_animation.setEndValue(0)
        self.fade_animation.finished.connect(self.hide)
        self.fade_animation.start()
        
    def filter_actions(self, text: str):
        """Filter actions based on search text"""
        text = text.lower()
        
        # Show/hide based on search
        notes_visible = not text or "notes" in text or "note" in text or "editor" in text
        quick_visible = not text or "quick" in text or "speech" in text or "voice" in text
        
        self.notes_action.setVisible(notes_visible)
        self.quick_action.setVisible(quick_visible)
        
    def update_app_status(self, notes_running: bool, quick_running: bool):
        """Update the running status of applications"""
        self.notes_running = notes_running
        self.quick_running = quick_running
        
        # Update button states
        self.notes_action.setEnabled(not notes_running)
        self.quick_action.setEnabled(not quick_running)
        
        # Update button styling based on state
        if notes_running:
            self.notes_action.setStyleSheet("""
                QPushButton#action_button:disabled {
                    background: rgba(76, 175, 80, 0.1);
                    border: 1px solid rgba(76, 175, 80, 0.3);
                    color: #4caf50;
                }
            """)
        
        if quick_running:
            self.quick_action.setStyleSheet("""
                QPushButton#action_button:disabled {
                    background: rgba(33, 150, 243, 0.1);
                    border: 1px solid rgba(33, 150, 243, 0.3);
                    color: #2196f3;
                }
            """)
    
    def on_launch_notes(self):
        """Handle Notes launch request"""
        if not self.notes_running:
            self.launch_notes.emit()
            self.close_palette()
    
    def on_launch_quick(self):
        """Handle Quick launch request"""
        if not self.quick_running:
            self.launch_quick.emit()
            self.close_palette()
    
    def close_palette(self):
        """Close the palette"""
        self.palette_closed.emit()
        self.hide_animated()
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Escape:
            self.close_palette()
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Execute first visible and enabled action
            if self.notes_action.isVisible() and self.notes_action.isEnabled():
                self.on_launch_notes()
            elif self.quick_action.isVisible() and self.quick_action.isEnabled():
                self.on_launch_quick()
        else:
            super().keyPressEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse press - close if clicking outside card"""
        if not self.card.geometry().contains(event.pos()):
            self.close_palette()
        else:
            super().mousePressEvent(event)


class PaletteManager:
    """Manager for the command palette system"""
    
    def __init__(self):
        self.logger = logging.getLogger('mumble.palette.manager')
        self.palette: Optional[CommandPalette] = None
        self.notes_process: Optional[subprocess.Popen] = None
        self.quick_process: Optional[subprocess.Popen] = None
        
    def show_palette(self):
        """Show the command palette"""
        if self.palette is None:
            self.palette = CommandPalette()
            self.palette.launch_notes.connect(self.launch_notes)
            self.palette.launch_quick.connect(self.launch_quick)
            self.palette.palette_closed.connect(self.on_palette_closed)
        
        # Update status
        notes_running = self.notes_process is not None and self.notes_process.poll() is None
        quick_running = self.quick_process is not None and self.quick_process.poll() is None
        self.palette.update_app_status(notes_running, quick_running)
        
        self.palette.show_animated()
    
    def launch_notes(self):
        """Launch Mumble Notes"""
        try:
            if self.notes_process is None or self.notes_process.poll() is not None:
                notes_path = os.path.join(os.path.dirname(__file__), '..', 'mumble_notes', 'app.py')
                self.notes_process = subprocess.Popen([sys.executable, notes_path])
                self.logger.info("Launched Mumble Notes")
        except Exception as e:
            self.logger.error(f"Failed to launch Notes: {e}")
    
    def launch_quick(self):
        """Launch Mumble Quick"""
        try:
            if self.quick_process is None or self.quick_process.poll() is not None:
                quick_path = os.path.join(os.path.dirname(__file__), '..', 'mumble_quick', 'app.py')
                self.quick_process = subprocess.Popen([sys.executable, quick_path])
                self.logger.info("Launched Mumble Quick")
        except Exception as e:
            self.logger.error(f"Failed to launch Quick: {e}")
    
    def on_palette_closed(self):
        """Handle palette close"""
        self.logger.debug("Command palette closed")
    
    def cleanup(self):
        """Cleanup resources"""
        if self.notes_process:
            self.notes_process.terminate()
        if self.quick_process:
            self.quick_process.terminate()


def main():
    """Main entry point for testing the command palette"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for better cross-platform appearance
    
    # Set application-wide dark theme
    app.setStyleSheet(f"""
        QApplication {{
            background-color: {COLORS['background']};
        }}
    """)
    
    # Create and show palette
    manager = PaletteManager()
    manager.show_palette()
    
    try:
        sys.exit(app.exec_())
    finally:
        manager.cleanup()


if __name__ == '__main__':
    main() 