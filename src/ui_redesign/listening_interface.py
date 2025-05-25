"""
Modern Listening Interface - Animated Waveform UI
Beautiful card-based interface with animated waveform for speech recognition
"""

import sys
import math
import random
from typing import List
import logging

from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QFrame, QLabel
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QLinearGradient, QFont

from .styles import LISTENING_STYLE, COLORS, apply_shadow_effect, create_icon


class WaveformWidget(QFrame):
    """Custom widget for animated waveform visualization"""
    
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
        self.gradient.setColorAt(0, QColor(33, 150, 243))  # Blue
        self.gradient.setColorAt(0.5, QColor(103, 58, 183))  # Purple
        self.gradient.setColorAt(1, QColor(156, 39, 176))  # Magenta
        
        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        
    def start_animation(self):
        """Start the waveform animation"""
        self.is_animating = True
        self.animation_timer.start(50)  # 20 FPS
        
    def stop_animation(self):
        """Stop the waveform animation"""
        self.is_animating = False
        self.animation_timer.stop()
        
        # Animate bars down to zero
        for i in range(self.bar_count):
            self.target_bars[i] = 0.0
            
    def update_animation(self):
        """Update animation frame"""
        if not self.is_animating:
            # Animate down when stopped
            all_zero = True
            for i in range(self.bar_count):
                if self.bars[i] > 0.01:
                    self.bars[i] *= 0.9  # Decay
                    all_zero = False
                else:
                    self.bars[i] = 0.0
            
            if all_zero:
                self.animation_timer.stop()
        else:
            # Generate new target values for active animation
            self.phase += 0.2
            
            for i in range(self.bar_count):
                # Create wave pattern with random variation
                base_wave = math.sin(self.phase + i * 0.3) * 0.5 + 0.5
                noise = random.uniform(0.7, 1.3)
                
                # Different frequency bands for more realistic look
                if i < self.bar_count // 4:
                    # Low frequencies - more steady
                    self.target_bars[i] = base_wave * noise * 0.8
                elif i < 3 * self.bar_count // 4:
                    # Mid frequencies - most active
                    self.target_bars[i] = base_wave * noise
                else:
                    # High frequencies - more erratic
                    self.target_bars[i] = base_wave * noise * 0.6
                
                # Smooth interpolation toward target
                self.bars[i] += (self.target_bars[i] - self.bars[i]) * 0.3
        
        self.update()
        
    def paintEvent(self, event):
        """Paint the waveform"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate positions
        total_width = self.bar_count * (self.bar_width + self.bar_spacing) - self.bar_spacing
        start_x = (self.width() - total_width) // 2
        center_y = self.height() // 2
        
        # Set gradient brush
        brush = QBrush(self.gradient)
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        
        # Draw bars
        for i, height in enumerate(self.bars):
            x = start_x + i * (self.bar_width + self.bar_spacing)
            bar_height = int(height * self.max_height)
            
            # Draw bar from center, expanding up and down
            rect_y = center_y - bar_height // 2
            painter.drawRoundedRect(x, rect_y, self.bar_width, bar_height, 2, 2)


class ListeningInterface(QDialog):
    """Modern listening interface with animated waveform"""
    
    # Signals
    listening_cancelled = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger('mumble.ui.listening')
        
        self.init_ui()
        self.setup_animations()
        
    def init_ui(self):
        """Initialize the user interface"""
        # Window configuration
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        
        # Apply styling
        self.setStyleSheet(LISTENING_STYLE)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Card container
        self.card = QFrame()
        self.card.setObjectName("card")
        self.card.setFixedSize(460, 320)  # Increased size for better text visibility
        apply_shadow_effect(self.card, blur_radius=30, offset=(0, 15))
        
        # Card layout
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(40, 35, 40, 35)  # Adjusted margins
        card_layout.setSpacing(25)  # Reduced spacing for better fit
        
        # Header with glowing text
        header = QLabel("Listening...")
        header.setObjectName("listening_header")
        header.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(header)
        
        # Waveform visualization
        self.waveform = WaveformWidget()
        card_layout.addWidget(self.waveform, alignment=Qt.AlignCenter)
        
        # Instruction text
        instruction = QLabel("Hold Ctrl+Alt to record • Release to send • Press Esc to cancel")
        instruction.setObjectName("instruction")
        instruction.setAlignment(Qt.AlignCenter)
        instruction.setWordWrap(True)  # Enable word wrapping
        instruction.setMaximumWidth(380)  # Ensure it fits within the card
        card_layout.addWidget(instruction)
        
        # Add card to main layout
        main_layout.addWidget(self.card, alignment=Qt.AlignCenter)
        self.setLayout(main_layout)
        
    def setup_animations(self):
        """Setup entrance and exit animations"""
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self.scale_animation = QPropertyAnimation(self.card, b"geometry")
        self.scale_animation.setDuration(400)
        self.scale_animation.setEasingCurve(QEasingCurve.OutBack)
        
    def show_listening(self):
        """Show the listening interface with animation"""
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
            final_rect.x() + 30,
            final_rect.y() + 30,
            final_rect.width() - 60,
            final_rect.height() - 60
        )
        
        self.scale_animation.setStartValue(start_rect)
        self.scale_animation.setEndValue(final_rect)
        self.scale_animation.start()
        
        # Start waveform animation
        self.waveform.start_animation()
        
    def hide_listening(self):
        """Hide the listening interface with animation"""
        # Stop waveform first
        self.waveform.stop_animation()
        
        # Animate fade out
        self.fade_animation.setStartValue(1)
        self.fade_animation.setEndValue(0)
        self.fade_animation.finished.connect(self.hide)
        self.fade_animation.start()
        
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Escape:
            self.listening_cancelled.emit()
            self.hide_listening()
        else:
            super().keyPressEvent(event)
            
    def mousePressEvent(self, event):
        """Handle mouse press - close if clicking outside card"""
        if not self.card.geometry().contains(event.pos()):
            self.listening_cancelled.emit()
            self.hide_listening()
        else:
            super().mousePressEvent(event)


class ListeningManager:
    """Manager for the listening interface"""
    
    def __init__(self):
        self.logger = logging.getLogger('mumble.listening.manager')
        self.interface = None
        self.is_listening = False
        
    def start_listening(self):
        """Start listening mode"""
        if not self.is_listening:
            self.is_listening = True
            
            if self.interface is None:
                self.interface = ListeningInterface()
                self.interface.listening_cancelled.connect(self.stop_listening)
            
            self.interface.show_listening()
            self.logger.info("Started listening interface")
    
    def stop_listening(self):
        """Stop listening mode"""
        if self.is_listening:
            self.is_listening = False
            
            if self.interface:
                self.interface.hide_listening()
            
            self.logger.info("Stopped listening interface")
    
    def is_active(self):
        """Check if listening interface is active"""
        return self.is_listening and self.interface and self.interface.isVisible()
    
    def cleanup(self):
        """Cleanup resources"""
        if self.interface:
            self.interface.close()


def main():
    """Main entry point for testing the listening interface"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set dark background for testing
    app.setStyleSheet(f"""
        QApplication {{
            background-color: {COLORS['background']};
        }}
    """)
    
    # Create and show listening interface
    manager = ListeningManager()
    
    # Show interface for 5 seconds
    QTimer.singleShot(100, manager.start_listening)
    QTimer.singleShot(5000, manager.stop_listening)
    
    try:
        sys.exit(app.exec_())
    finally:
        manager.cleanup()


if __name__ == '__main__':
    main() 