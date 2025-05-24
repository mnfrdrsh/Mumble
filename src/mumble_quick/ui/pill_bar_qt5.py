"""
Animated pill-shaped bar UI for Mumble Quick using PyQt5
Modern Qt-based replacement for the Tkinter implementation
"""

import sys
import math
import random
from typing import List, Optional
import logging
import traceback

from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QFrame)
from PyQt5.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor, QPainterPath, QBrush, QFont, QPolygon


class WaveformBar(QWidget):
    """A pill-shaped bar with animated waveform visualization using PyQt5"""
    
    # Signal for when the close button is clicked
    close_requested = pyqtSignal()
    
    def __init__(self):
        try:
            super().__init__()
            self.logger = logging.getLogger('mumble.quick.ui')
            self.logger.info("Initializing PyQt5 WaveformBar")
            
            # Configure window
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.setFixedSize(120, 20)
            
            # Initialize waveform variables
            self.points: List[float] = [0.0] * 20  # Points for the waveform
            self.is_listening = False
            self.animation_timer: Optional[QTimer] = None
            
            # Colors
            self.bg_color = QColor(44, 44, 44)  # #2C2C2C
            self.border_color = QColor(60, 60, 60)  # #3C3C3C
            self.waveform_color = QColor(76, 175, 80)  # #4CAF50
            self.close_color = QColor(128, 128, 128)  # #808080
            
            # Animation timer
            self.animation_timer = QTimer()
            self.animation_timer.timeout.connect(self._animate_waveform)
            
            # Drag variables
            self._drag_start_position = None
            
            self.logger.info("PyQt5 WaveformBar initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing PyQt5 WaveformBar: {e}")
            self.logger.error(traceback.format_exc())
            raise
    
    def paintEvent(self, event):
        """Custom paint event to draw the pill shape and waveform"""
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Create pill shape path
            rect = self.rect()
            radius = 10
            
            path = QPainterPath()
            path.addRoundedRect(rect, radius, radius)
            
            # Fill background
            painter.fillPath(path, QBrush(self.bg_color))
            
            # Draw border
            painter.setPen(QPen(self.border_color, 1))
            painter.drawPath(path)
            
            # Draw waveform if listening
            if self.is_listening:
                self._draw_waveform(painter)
            
            # Draw close button
            self._draw_close_button(painter)
            
        except Exception as e:
            self.logger.error(f"Error in paintEvent: {e}")
            self.logger.error(traceback.format_exc())
    
    def _draw_waveform(self, painter):
        """Draw the animated waveform"""
        try:
            painter.setPen(QPen(self.waveform_color, 2))
            
            # Create smooth curve through points
            x_step = 120.0 / (len(self.points) - 1)
            
            # Draw line segments for waveform
            for i in range(len(self.points) - 1):
                x1 = i * x_step
                y1 = 10 + self.points[i]  # Center line at 10 (half of 20px height)
                x2 = (i + 1) * x_step
                y2 = 10 + self.points[i + 1]
                
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))
                
        except Exception as e:
            self.logger.error(f"Error drawing waveform: {e}")
            self.logger.error(traceback.format_exc())
    
    def _draw_close_button(self, painter):
        """Draw the close button"""
        try:
            size = 12
            padding = 4
            x = 120 - size - padding
            y = padding
            
            painter.setPen(QPen(self.close_color, 1))
            painter.setFont(QFont("Arial", 8))
            painter.drawText(x, y, size, size, Qt.AlignCenter, "×")
            
        except Exception as e:
            self.logger.error(f"Error drawing close button: {e}")
            self.logger.error(traceback.format_exc())
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging and close button"""
        try:
            if event.button() == Qt.LeftButton:
                # Check if close button was clicked
                size = 12
                padding = 4
                close_x = 120 - size - padding
                close_y = padding
                
                if (close_x <= event.x() <= close_x + size and 
                    close_y <= event.y() <= close_y + size):
                    self.close_requested.emit()
                    return
                
                # Start dragging
                self._drag_start_position = event.globalPos() - self.pos()
                
        except Exception as e:
            self.logger.error(f"Error in mousePressEvent: {e}")
            self.logger.error(traceback.format_exc())
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        try:
            if (event.buttons() == Qt.LeftButton and 
                self._drag_start_position is not None):
                self.move(event.globalPos() - self._drag_start_position)
                
        except Exception as e:
            self.logger.error(f"Error in mouseMoveEvent: {e}")
            self.logger.error(traceback.format_exc())
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        self._drag_start_position = None
    
    def show(self):
        """Show the bar with animation"""
        try:
            self.logger.info("Showing PyQt5 WaveformBar")
            
            # Get screen geometry
            desktop = QApplication.desktop()
            screen = desktop.screenGeometry()
            screen_width = screen.width()
            screen_height = screen.height()
            
            # Position window at bottom center of screen
            x = (screen_width - 120) // 2
            y = screen_height - 100  # 100 pixels from bottom
            
            self.move(x, y)
            super().show()
            self.raise_()
            self.activateWindow()
            
            self.start_animation()
            self.logger.info(f"PyQt5 WaveformBar shown at position ({x}, {y})")
            
        except Exception as e:
            self.logger.error(f"Error showing PyQt5 WaveformBar: {e}")
            self.logger.error(traceback.format_exc())
    
    def hide(self):
        """Hide the bar and stop animation"""
        try:
            self.logger.info("Hiding PyQt5 WaveformBar")
            self.stop_animation()
            super().hide()
            self.logger.info("PyQt5 WaveformBar hidden")
            
        except Exception as e:
            self.logger.error(f"Error hiding PyQt5 WaveformBar: {e}")
            self.logger.error(traceback.format_exc())
    
    def start_animation(self):
        """Start the waveform animation"""
        try:
            if not self.is_listening:
                self.is_listening = True
                self.logger.info("Starting waveform animation")
                self.animation_timer.start(50)  # 50ms interval for smooth animation
                
        except Exception as e:
            self.logger.error(f"Error starting animation: {e}")
            self.logger.error(traceback.format_exc())
    
    def stop_animation(self):
        """Stop the waveform animation"""
        try:
            self.is_listening = False
            if self.animation_timer:
                self.animation_timer.stop()
            self.logger.info("Stopped waveform animation")
            
        except Exception as e:
            self.logger.error(f"Error stopping animation: {e}")
            self.logger.error(traceback.format_exc())
    
    def _animate_waveform(self):
        """Animate the waveform points"""
        try:
            if not self.is_listening:
                return
            
            # Update points with smooth transitions
            for i in range(len(self.points)):
                target = random.uniform(-5.0, 5.0)
                self.points[i] += (target - self.points[i]) * 0.3
            
            # Trigger repaint
            self.update()
            
        except Exception as e:
            self.logger.error(f"Error in waveform animation: {e}")
            self.logger.error(traceback.format_exc())
    
    def closeEvent(self, event):
        """Handle window close event"""
        try:
            self.stop_animation()
            event.accept()
            
        except Exception as e:
            self.logger.error(f"Error in closeEvent: {e}")
            self.logger.error(traceback.format_exc())
            event.accept()


# Test application for the waveform bar
if __name__ == '__main__':
    import sys
    
    app = QApplication(sys.argv)
    
    # Create and show the waveform bar
    waveform = WaveformBar()
    waveform.close_requested.connect(app.quit)
    waveform.show()
    
    # Start animation for testing
    waveform.start_animation()
    
    sys.exit(app.exec_()) 