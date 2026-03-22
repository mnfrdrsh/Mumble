"""
Command palette for the canonical Qt Mumble app.
"""

import logging
import sys
from typing import Optional

from PyQt5.QtCore import QEasingCurve, Qt, QPropertyAnimation, pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from .styles import COLORS, LAUNCHER_STYLE, apply_shadow_effect, create_icon


class ActionButton(QPushButton):
    """Custom action button with icon, text, and status label."""

    def __init__(self, icon_text: str, main_text: str, hotkey: str = "", enabled: bool = True):
        super().__init__()
        self.setObjectName("action_button")
        self.setEnabled(enabled)

        layout = QHBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)

        icon_label = create_icon(icon_text, size=20, color=COLORS["text_secondary"])
        layout.addWidget(icon_label)

        text_label = QLabel(main_text)
        text_label.setStyleSheet(
            f"""
            color: {COLORS['text_primary'] if enabled else COLORS['text_muted']};
            font-weight: 500;
        """
        )
        layout.addWidget(text_label)

        layout.addStretch()

        if hotkey:
            hotkey_label = QLabel(hotkey)
            hotkey_label.setObjectName("hotkey")
            layout.addWidget(hotkey_label)

        self.setLayout(layout)
        self.setFixedHeight(56)


class CommandPalette(QDialog):
    """Main command palette interface."""

    launch_notes = pyqtSignal()
    launch_quick = pyqtSignal()
    palette_closed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger("mumble.ui.palette")
        self.notes_running = False
        self.quick_running = False

        self.init_ui()
        self.setup_animations()
        self.setup_shortcuts()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setModal(False)
        self.setStyleSheet(LAUNCHER_STYLE)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 24, 24, 24)

        self.card = QFrame()
        self.card.setObjectName("card")
        self.card.setFixedSize(480, 420)
        apply_shadow_effect(self.card)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(32, 32, 32, 32)
        card_layout.setSpacing(24)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        app_icon = create_icon("M", size=24, color=COLORS["accent_blue"])
        header_layout.addWidget(app_icon)

        title = QLabel("Mumble Launcher")
        title.setObjectName("header")
        header_layout.addWidget(title)

        header_layout.addStretch()
        card_layout.addLayout(header_layout)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("search")
        self.search_input.setPlaceholderText("launch mumble...")
        self.search_input.textChanged.connect(self.filter_actions)
        card_layout.addWidget(self.search_input)

        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(8)

        self.notes_action = ActionButton(
            "N", "Open Mumble Notes", "Notes", enabled=not self.notes_running
        )
        self.notes_action.clicked.connect(self.on_launch_notes)
        actions_layout.addWidget(self.notes_action)

        self.quick_action = ActionButton(
            "Q", "Start Quick Dictation", "Ctrl+Alt+Space", enabled=not self.quick_running
        )
        self.quick_action.clicked.connect(self.on_launch_quick)
        actions_layout.addWidget(self.quick_action)

        card_layout.addLayout(actions_layout)

        warning_layout = QHBoxLayout()
        warning_icon = create_icon("!", size=16, color=COLORS["warning"])
        warning_layout.addWidget(warning_icon)

        warning_text = QLabel("Quick dictation inserts into the active app or Notes.")
        warning_text.setObjectName("warning")
        warning_layout.addWidget(warning_text)
        warning_layout.addStretch()

        card_layout.addLayout(warning_layout)

        main_layout.addWidget(self.card, alignment=Qt.AlignCenter)
        self.setLayout(main_layout)
        self.setFixedSize(self.sizeHint())
        self.search_input.setFocus()

    def setup_animations(self):
        """Setup entrance and exit animations."""
        self._hide_on_fade = False
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_animation.finished.connect(self.on_fade_finished)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        self.escape_shortcut = QKeySequence("Esc")

    def show_animated(self):
        """Show the palette with animation."""
        screen = QApplication.desktop().screenGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2,
        )

        self._hide_on_fade = False
        self.setWindowOpacity(0)
        self.show()

        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.start()

    def hide_animated(self):
        """Hide the palette with animation."""
        self._hide_on_fade = True
        self.fade_animation.setStartValue(1)
        self.fade_animation.setEndValue(0)
        self.fade_animation.start()

    def on_fade_finished(self):
        """Hide the dialog only after fade-out completes."""
        if self._hide_on_fade:
            self.hide()

    def filter_actions(self, text: str):
        """Filter actions based on search text."""
        text = text.lower()

        notes_visible = not text or "notes" in text or "note" in text or "editor" in text
        quick_visible = not text or "quick" in text or "speech" in text or "voice" in text

        self.notes_action.setVisible(notes_visible)
        self.quick_action.setVisible(quick_visible)

    def update_app_status(self, notes_running: bool, quick_running: bool):
        """Update the running status displayed in the palette."""
        self.notes_running = notes_running
        self.quick_running = quick_running

        self.notes_action.setEnabled(not notes_running)
        self.quick_action.setEnabled(not quick_running)

        if notes_running:
            self.notes_action.setStyleSheet(
                """
                QPushButton#action_button:disabled {
                    background: rgba(76, 175, 80, 0.1);
                    border: 1px solid rgba(76, 175, 80, 0.3);
                    color: #4caf50;
                }
            """
            )
        else:
            self.notes_action.setStyleSheet("")

        if quick_running:
            self.quick_action.setStyleSheet(
                """
                QPushButton#action_button:disabled {
                    background: rgba(33, 150, 243, 0.1);
                    border: 1px solid rgba(33, 150, 243, 0.3);
                    color: #2196f3;
                }
            """
            )
        else:
            self.quick_action.setStyleSheet("")

    def on_launch_notes(self):
        """Handle Notes launch request."""
        if not self.notes_running:
            self.launch_notes.emit()
            self.close_palette()

    def on_launch_quick(self):
        """Handle Quick launch request."""
        if not self.quick_running:
            self.launch_quick.emit()
            self.close_palette()

    def close_palette(self):
        """Close the palette."""
        self.palette_closed.emit()
        self.hide_animated()

    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Escape:
            self.close_palette()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if self.notes_action.isVisible() and self.notes_action.isEnabled():
                self.on_launch_notes()
            elif self.quick_action.isVisible() and self.quick_action.isEnabled():
                self.on_launch_quick()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        """Allow interaction without dismissing the palette on stray clicks."""
        super().mousePressEvent(event)


class PaletteManager:
    """Manager for the in-process Qt command palette."""

    def __init__(self):
        self.logger = logging.getLogger("mumble.palette.manager")
        self.palette: Optional[CommandPalette] = None

    def show_palette(self):
        """Show the command palette."""
        if self.palette is None:
            self.palette = CommandPalette()
            self.palette.palette_closed.connect(self.on_palette_closed)

        # Notes and quick mode now run in-process in the canonical Qt app.
        self.palette.update_app_status(False, False)
        self.palette.show_animated()
        if hasattr(self.palette, "raise_"):
            self.palette.raise_()
        if hasattr(self.palette, "activateWindow"):
            self.palette.activateWindow()
        if hasattr(self.palette, "search_input"):
            self.palette.search_input.clear()
            self.palette.search_input.setFocus()

    def on_palette_closed(self):
        """Handle palette close."""
        self.logger.debug("Command palette closed")

    def cleanup(self):
        """Cleanup resources."""
        if self.palette:
            self.palette.close()
            self.palette = None


def main():
    """Main entry point for testing the command palette."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(
        f"""
        QApplication {{
            background-color: {COLORS['background']};
        }}
    """
    )

    manager = PaletteManager()
    manager.show_palette()

    try:
        sys.exit(app.exec_())
    finally:
        manager.cleanup()


if __name__ == "__main__":
    main()
