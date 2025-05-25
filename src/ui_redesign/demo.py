"""
Demo Script for Modern Mumble UI
Showcases all the new UI components for testing and presentation
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from .command_palette import PaletteManager
from .listening_interface import ListeningManager
from .notes_editor import NotesManager
from .styles import COLORS, LAUNCHER_STYLE


class DemoController(QWidget):
    """Demo controller window for testing UI components"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mumble UI Demo Controller")
        self.setFixedSize(400, 300)
        
        # Managers
        self.palette_manager = PaletteManager()
        self.listening_manager = ListeningManager()
        self.notes_manager = NotesManager()
        
        self.init_ui()
        self.center_window()
        
    def init_ui(self):
        """Initialize the demo controller UI"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Mumble UI Demo")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Test the new modern interface components")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: gray;")
        layout.addWidget(subtitle)
        
        layout.addStretch()
        
        # Demo buttons
        palette_btn = QPushButton("Show Command Palette")
        palette_btn.clicked.connect(self.show_palette)
        palette_btn.setFixedHeight(40)
        layout.addWidget(palette_btn)
        
        listening_btn = QPushButton("Show Listening Interface")
        listening_btn.clicked.connect(self.show_listening)
        listening_btn.setFixedHeight(40)
        layout.addWidget(listening_btn)
        
        notes_btn = QPushButton("Show Notes Editor")
        notes_btn.clicked.connect(self.show_notes)
        notes_btn.setFixedHeight(40)
        layout.addWidget(notes_btn)
        
        layout.addStretch()
        
        # Demo sequence button
        demo_btn = QPushButton("▶ Run Full Demo Sequence")
        demo_btn.clicked.connect(self.run_demo_sequence)
        demo_btn.setFixedHeight(50)
        demo_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2196f3, stop:1 #9c27b0);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1976d2, stop:1 #7b1fa2);
            }
        """)
        layout.addWidget(demo_btn)
        
        # Instructions
        instructions = QLabel("• Command Palette: Central hub for launching apps\n"
                             "• Listening Interface: Beautiful waveform during speech recognition\n"
                             "• Notes Editor: Modern card-based notes interface")
        instructions.setStyleSheet("color: gray; font-size: 11px;")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        self.setLayout(layout)
        
        # Apply styling
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border-color: #bbb;
            }
        """)
    
    def center_window(self):
        """Center the window on screen"""
        screen = QApplication.desktop().screenGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
    
    def show_palette(self):
        """Show the command palette"""
        self.palette_manager.show_palette()
    
    def show_listening(self):
        """Show the listening interface"""
        self.listening_manager.start_listening()
        
        # Auto-hide after 5 seconds for demo
        QTimer.singleShot(5000, self.listening_manager.stop_listening)
    
    def show_notes(self):
        """Show the notes editor"""
        sample_text = ("Welcome to Mumble Notes!\n\n"
                      "This is the new modern notes editor with:\n"
                      "• Beautiful card-based design\n"
                      "• Dark theme with glassmorphism effects\n"
                      "• Save, copy, and close functionality\n"
                      "• Keyboard shortcuts support\n\n"
                      "Try editing this text and using the buttons below!")
        
        self.notes_manager.open_editor(sample_text)
    
    def run_demo_sequence(self):
        """Run a full demo sequence showing all components"""
        # Hide demo controller temporarily
        self.hide()
        
        # 1. Show command palette first
        QTimer.singleShot(500, self.show_palette)
        
        # 2. Close palette and show listening interface
        QTimer.singleShot(3000, self.close_palette_if_open)
        QTimer.singleShot(3500, self.show_listening)
        
        # 3. Show notes editor
        QTimer.singleShot(8000, self.show_notes)
        
        # 4. Show demo controller again
        QTimer.singleShot(10000, self.show)
    
    def close_palette_if_open(self):
        """Close palette if it's open"""
        if self.palette_manager.palette:
            self.palette_manager.palette.close_palette()
    
    def cleanup(self):
        """Cleanup resources"""
        self.palette_manager.cleanup()
        self.listening_manager.cleanup()
        self.notes_manager.cleanup()


def main():
    """Main demo entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application properties
    app.setApplicationName("Mumble UI Demo")
    app.setApplicationVersion("2.0")
    
    print("=" * 60)
    print("🎨 MUMBLE UI REDESIGN DEMO")
    print("=" * 60)
    print("✨ Features:")
    print("  • Modern Command Palette with glassmorphism design")
    print("  • Animated Listening Interface with beautiful waveforms")
    print("  • Card-based Notes Editor with modern styling")
    print("  • Dark theme with blue/purple gradient accents")
    print("  • Smooth animations and transitions")
    print("")
    print("🎯 Demo Controls:")
    print("  • Individual component testing buttons")
    print("  • Full demo sequence showcase")
    print("  • ESC key to close any interface")
    print("")
    print("🎮 Interactive Elements:")
    print("  • Type in the command palette search")
    print("  • Watch the animated waveform")
    print("  • Edit, save, and copy notes")
    print("=" * 60)
    
    # Create and show demo controller
    demo = DemoController()
    demo.show()
    
    try:
        result = app.exec_()
        demo.cleanup()
        return result
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
        demo.cleanup()
        return 0


if __name__ == '__main__':
    sys.exit(main()) 