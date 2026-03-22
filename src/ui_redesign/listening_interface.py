"""
Modern Listening Interface - Animated Waveform UI
Beautiful card-based interface with animated waveform for speech recognition
"""

import sys
import math
import random
import logging

from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QFrame, QLabel
from PyQt5.QtCore import QObject, Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QBrush, QLinearGradient

from .styles import LISTENING_STYLE, COLORS, apply_shadow_effect


class WaveformWidget(QFrame):
    """Custom widget for animated waveform visualization."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(320, 80)

        # Waveform configuration
        self.bar_count = 40
        self.bar_width = 4
        self.bar_spacing = 4
        self.max_height = 60

        # Animation state
        self.bars = [0.0] * self.bar_count
        self.target_bars = [0.0] * self.bar_count
        self.phase = 0.0
        self.is_animating = False

        # Colors
        self.gradient = QLinearGradient(0, 0, self.width(), 0)
        self.gradient.setColorAt(0, QColor(33, 150, 243))
        self.gradient.setColorAt(0.5, QColor(103, 58, 183))
        self.gradient.setColorAt(1, QColor(156, 39, 176))

        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)

    def start_animation(self):
        """Start the waveform animation."""
        self.is_animating = True
        self.animation_timer.start(50)

    def stop_animation(self):
        """Stop the waveform animation."""
        self.is_animating = False
        self.animation_timer.stop()

        for index in range(self.bar_count):
            self.target_bars[index] = 0.0

    def update_animation(self):
        """Update the animation frame."""
        if not self.is_animating:
            all_zero = True
            for index in range(self.bar_count):
                if self.bars[index] > 0.01:
                    self.bars[index] *= 0.9
                    all_zero = False
                else:
                    self.bars[index] = 0.0

            if all_zero:
                self.animation_timer.stop()
        else:
            self.phase += 0.2

            for index in range(self.bar_count):
                base_wave = math.sin(self.phase + index * 0.3) * 0.5 + 0.5
                noise = random.uniform(0.7, 1.3)

                if index < self.bar_count // 4:
                    self.target_bars[index] = base_wave * noise * 0.8
                elif index < 3 * self.bar_count // 4:
                    self.target_bars[index] = base_wave * noise
                else:
                    self.target_bars[index] = base_wave * noise * 0.6

                self.bars[index] += (self.target_bars[index] - self.bars[index]) * 0.3

        self.update()

    def paintEvent(self, event):
        """Paint the waveform."""
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        total_width = self.bar_count * (self.bar_width + self.bar_spacing) - self.bar_spacing
        start_x = (self.width() - total_width) // 2
        center_y = self.height() // 2

        painter.setBrush(QBrush(self.gradient))
        painter.setPen(Qt.NoPen)

        for index, height in enumerate(self.bars):
            x = start_x + index * (self.bar_width + self.bar_spacing)
            bar_height = int(height * self.max_height)
            rect_y = center_y - bar_height // 2
            painter.drawRoundedRect(x, rect_y, self.bar_width, bar_height, 2, 2)


class ListeningInterface(QDialog):
    """Modern listening interface with animated waveform."""

    listening_cancelled = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger("mumble.ui.listening")

        self.init_ui()
        self.setup_animations()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setModal(True)
        self.setStyleSheet(LISTENING_STYLE)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)

        self.card = QFrame()
        self.card.setObjectName("card")
        self.card.setFixedSize(460, 320)
        apply_shadow_effect(self.card, blur_radius=30, offset=(0, 15))

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(40, 35, 40, 35)
        card_layout.setSpacing(25)

        header = QLabel("Listening...")
        header.setObjectName("listening_header")
        header.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(header)

        self.waveform = WaveformWidget()
        card_layout.addWidget(self.waveform, alignment=Qt.AlignCenter)

        instruction = QLabel("Speak your dictation. Press Ctrl+Alt+Space or Esc to cancel.")
        instruction.setObjectName("instruction")
        instruction.setAlignment(Qt.AlignCenter)
        instruction.setWordWrap(True)
        instruction.setMaximumWidth(380)
        card_layout.addWidget(instruction)

        main_layout.addWidget(self.card, alignment=Qt.AlignCenter)
        self.setLayout(main_layout)
        self.setFixedSize(self.sizeHint())

    def setup_animations(self):
        """Setup entrance and exit animations."""
        self._hide_on_fade = False

        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_animation.finished.connect(self.on_fade_finished)

    def show_listening(self):
        """Show the listening interface with animation."""
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

        self.waveform.start_animation()

    def hide_listening(self):
        """Hide the listening interface with animation."""
        self.waveform.stop_animation()
        self._hide_on_fade = True
        self.fade_animation.setStartValue(1)
        self.fade_animation.setEndValue(0)
        self.fade_animation.start()

    def on_fade_finished(self):
        """Hide the dialog after fade-out completes."""
        if self._hide_on_fade:
            self.hide()

    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Escape:
            self.listening_cancelled.emit()
            self.hide_listening()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        """Close if the user clicks outside the card."""
        if not self.card.geometry().contains(event.pos()):
            self.listening_cancelled.emit()
            self.hide_listening()
        else:
            super().mousePressEvent(event)


class ListeningManager(QObject):
    """Manager for the listening interface."""

    listening_cancelled = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("mumble.listening.manager")
        self.interface = None
        self.is_listening = False

    def start_listening(self):
        """Start listening mode."""
        if self.is_listening:
            return

        self.is_listening = True

        if self.interface is None:
            self.interface = ListeningInterface()
            self.interface.listening_cancelled.connect(self.on_listening_cancelled)

        self.interface.show_listening()
        self.logger.info("Started listening interface")

    def stop_listening(self):
        """Stop listening mode."""
        if not self.is_listening:
            return

        self.is_listening = False

        if self.interface:
            self.interface.hide_listening()

        self.logger.info("Stopped listening interface")

    def on_listening_cancelled(self):
        """Stop listening and notify application-level listeners."""
        self.stop_listening()
        self.listening_cancelled.emit()

    def is_active(self):
        """Check if the listening interface is active."""
        return bool(self.is_listening and self.interface and self.interface.isVisible())

    def cleanup(self):
        """Cleanup resources."""
        if self.interface:
            self.interface.close()


def main():
    """Main entry point for testing the listening interface."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    app.setStyleSheet(
        f"""
        QApplication {{
            background-color: {COLORS['background']};
        }}
    """
    )

    manager = ListeningManager()

    QTimer.singleShot(100, manager.start_listening)
    QTimer.singleShot(5000, manager.stop_listening)

    try:
        sys.exit(app.exec_())
    finally:
        manager.cleanup()


if __name__ == "__main__":
    main()
