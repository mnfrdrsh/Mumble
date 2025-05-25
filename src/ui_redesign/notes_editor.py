"""
Modern Notes Editor - Card-based Interface
Beautiful notes editor with modern UI and glassmorphism design
"""

import sys
import os
import logging
from typing import Optional
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, 
    QLabel, QPlainTextEdit, QPushButton, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QTextCursor, QKeySequence
import pyperclip

from .styles import NOTES_STYLE, COLORS, apply_shadow_effect, create_icon


class NotesEditor(QWidget):
    """Modern notes editor with card-based design"""
    
    # Signals
    note_saved = pyqtSignal(str)  # Emitted when note is saved
    note_copied = pyqtSignal(str)  # Emitted when note is copied
    editor_closed = pyqtSignal()  # Emitted when editor is closed
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger('mumble.ui.notes')
        
        # State
        self.current_note_text = ""
        self.is_modified = False
        
        self.init_ui()
        self.setup_shortcuts()
        
    def init_ui(self):
        """Initialize the user interface"""
        # Window configuration
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Apply styling
        self.setStyleSheet(NOTES_STYLE)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Card container
        self.card = QFrame()
        self.card.setObjectName("card")
        self.card.setFixedSize(600, 500)
        apply_shadow_effect(self.card)
        
        # Card layout
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(32, 32, 32, 32)
        card_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)
        
        # App icon
        app_icon = create_icon("📝", size=24, color=COLORS['accent_blue'])
        header_layout.addWidget(app_icon)
        
        # Title
        title = QLabel("Mumble Notes")
        title.setObjectName("notes_header")
        header_layout.addWidget(title)
        
        # Spacer
        header_layout.addStretch()
        
        # Options button (future feature)
        options_btn = QPushButton("⋯")
        options_btn.setObjectName("close_button")
        options_btn.setFixedSize(32, 32)
        options_btn.setStyleSheet("""
            QPushButton {
                border-radius: 16px;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(options_btn)
        
        card_layout.addLayout(header_layout)
        
        # Text editor
        self.text_editor = QPlainTextEdit()
        self.text_editor.setObjectName("editor")
        self.text_editor.setPlaceholderText("Write your notes here...")
        self.text_editor.textChanged.connect(self.on_text_changed)
        
        # Set up editor properties
        font = QFont("Inter, Segoe UI, Roboto", 13)
        font.setWeight(400)
        self.text_editor.setFont(font)
        
        card_layout.addWidget(self.text_editor)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(16)
        
        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.setObjectName("save_button")
        self.save_button.clicked.connect(self.save_note)
        self.save_button.setFixedHeight(44)
        buttons_layout.addWidget(self.save_button)
        
        # Copy button
        self.copy_button = QPushButton("Copy")
        self.copy_button.setObjectName("copy_button")
        self.copy_button.clicked.connect(self.copy_note)
        self.copy_button.setFixedHeight(44)
        buttons_layout.addWidget(self.copy_button)
        
        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.setObjectName("close_button")
        self.close_button.clicked.connect(self.close_editor)
        self.close_button.setFixedHeight(44)
        buttons_layout.addWidget(self.close_button)
        
        card_layout.addLayout(buttons_layout)
        
        # Add card to main layout
        main_layout.addWidget(self.card, alignment=Qt.AlignCenter)
        self.setLayout(main_layout)
        
        # Set initial focus
        self.text_editor.setFocus()
        
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Save: Ctrl+S
        save_shortcut = QKeySequence.Save
        # Copy: Ctrl+C (handled by text editor)
        # Close: Ctrl+W or Escape
        
    def on_text_changed(self):
        """Handle text changes"""
        current_text = self.text_editor.toPlainText()
        self.is_modified = current_text != self.current_note_text
        
        # Update save button appearance if needed
        if self.is_modified:
            self.save_button.setText("Save *")
        else:
            self.save_button.setText("Save")
    
    def save_note(self):
        """Save the current note"""
        text = self.text_editor.toPlainText().strip()
        
        if not text:
            self.logger.warning("Attempted to save empty note")
            return
        
        try:
            # Create notes directory if it doesn't exist
            notes_dir = os.path.expanduser("~/Documents/Mumble Notes")
            os.makedirs(notes_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"note_{timestamp}.txt"
            filepath = os.path.join(notes_dir, filename)
            
            # Save file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text)
            
            self.current_note_text = text
            self.is_modified = False
            self.save_button.setText("Save")
            
            self.logger.info(f"Note saved to {filepath}")
            self.note_saved.emit(filepath)
            
            # Show brief success feedback
            self.show_save_feedback()
            
        except Exception as e:
            self.logger.error(f"Failed to save note: {e}")
    
    def copy_note(self):
        """Copy note content to clipboard"""
        text = self.text_editor.toPlainText().strip()
        
        if not text:
            self.logger.warning("Attempted to copy empty note")
            return
        
        try:
            pyperclip.copy(text)
            self.logger.info("Note copied to clipboard")
            self.note_copied.emit(text)
            
            # Show brief success feedback
            self.show_copy_feedback()
            
        except Exception as e:
            self.logger.error(f"Failed to copy note: {e}")
    
    def close_editor(self):
        """Close the editor"""
        # TODO: Add unsaved changes warning if needed
        self.editor_closed.emit()
        self.close()
    
    def show_save_feedback(self):
        """Show brief visual feedback for save action"""
        original_text = self.save_button.text()
        self.save_button.setText("Saved ✓")
        self.save_button.setStyleSheet("""
            QPushButton#save_button {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4caf50, stop:1 #66bb6a);
            }
        """)
        
        # Reset after 1.5 seconds
        QTimer.singleShot(1500, lambda: self.reset_save_button(original_text))
    
    def show_copy_feedback(self):
        """Show brief visual feedback for copy action"""
        original_text = self.copy_button.text()
        self.copy_button.setText("Copied ✓")
        self.copy_button.setStyleSheet("""
            QPushButton#copy_button {
                background: rgba(33, 150, 243, 0.2);
                border: 2px solid #4caf50;
                color: #4caf50;
            }
        """)
        
        # Reset after 1.5 seconds
        QTimer.singleShot(1500, lambda: self.reset_copy_button(original_text))
    
    def reset_save_button(self, original_text):
        """Reset save button to original state"""
        self.save_button.setText(original_text)
        self.save_button.setStyleSheet("")  # Reset to default styling
    
    def reset_copy_button(self, original_text):
        """Reset copy button to original state"""
        self.copy_button.setText(original_text)
        self.copy_button.setStyleSheet("")  # Reset to default styling
    
    def set_text(self, text: str):
        """Set the editor text"""
        self.text_editor.setPlainText(text)
        self.current_note_text = text
        self.is_modified = False
        self.save_button.setText("Save")
        
        # Move cursor to end
        cursor = self.text_editor.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.text_editor.setTextCursor(cursor)
    
    def append_text(self, text: str):
        """Append text to the editor"""
        current_text = self.text_editor.toPlainText()
        if current_text and not current_text.endswith('\n'):
            text = '\n' + text
        
        self.text_editor.appendPlainText(text)
        self.text_editor.setFocus()
    
    def get_text(self) -> str:
        """Get the current editor text"""
        return self.text_editor.toPlainText()
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Escape:
            self.close_editor()
        elif event.matches(QKeySequence.Save):
            self.save_note()
        elif event.matches(QKeySequence.Close):
            self.close_editor()
        else:
            super().keyPressEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse press - allow dragging the window"""
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.globalPos() - self.pos()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for window dragging"""
        if hasattr(self, 'drag_start_position') and self.drag_start_position:
            if event.buttons() == Qt.LeftButton:
                self.move(event.globalPos() - self.drag_start_position)


class NotesManager:
    """Manager for the notes editor"""
    
    def __init__(self):
        self.logger = logging.getLogger('mumble.notes.manager')
        self.editor: Optional[NotesEditor] = None
        self.is_open = False
    
    def open_editor(self, initial_text: str = ""):
        """Open the notes editor"""
        if not self.is_open:
            self.editor = NotesEditor()
            self.editor.note_saved.connect(self.on_note_saved)
            self.editor.note_copied.connect(self.on_note_copied)
            self.editor.editor_closed.connect(self.on_editor_closed)
            
            if initial_text:
                self.editor.set_text(initial_text)
            
            # Center on screen
            screen = QApplication.desktop().screenGeometry()
            self.editor.move(
                (screen.width() - self.editor.width()) // 2,
                (screen.height() - self.editor.height()) // 2
            )
            
            self.editor.show()
            self.is_open = True
            self.logger.info("Notes editor opened")
    
    def close_editor(self):
        """Close the notes editor"""
        if self.is_open and self.editor:
            self.editor.close()
            self.on_editor_closed()
    
    def append_text(self, text: str):
        """Append text to the current editor (if open)"""
        if self.is_open and self.editor:
            self.editor.append_text(text)
        else:
            # Open editor with the text
            self.open_editor(text)
    
    def on_note_saved(self, filepath: str):
        """Handle note saved event"""
        self.logger.info(f"Note saved: {filepath}")
    
    def on_note_copied(self, text: str):
        """Handle note copied event"""
        self.logger.info("Note copied to clipboard")
    
    def on_editor_closed(self):
        """Handle editor closed event"""
        self.is_open = False
        self.editor = None
        self.logger.info("Notes editor closed")
    
    def is_editor_open(self) -> bool:
        """Check if editor is currently open"""
        return self.is_open and self.editor is not None
    
    def cleanup(self):
        """Cleanup resources"""
        if self.editor:
            self.editor.close()


def main():
    """Main entry point for testing the notes editor"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set dark background for testing
    app.setStyleSheet(f"""
        QApplication {{
            background-color: {COLORS['background']};
        }}
    """)
    
    # Create and show notes editor
    manager = NotesManager()
    manager.open_editor("This is a sample note for testing the editor interface.")
    
    try:
        sys.exit(app.exec_())
    finally:
        manager.cleanup()


if __name__ == '__main__':
    main() 