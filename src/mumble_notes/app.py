"""
Main application module for Mumble Notes
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.speech_recognition import SpeechRecognizer
from shared.logging import setup_logging
from ui.editor import RichTextEditor
from ui.document_manager import DocumentManager

class MumbleNotes:
    """Main application class for Mumble Notes"""
    
    def __init__(self):
        """Initialize the application"""
        self.logger = setup_logging('notes')
        self.root = tk.Tk()
        self.root.title("Mumble Notes")
        self.root.geometry("1200x800")
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use clam theme for better looking widgets
        
        # Configure grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Initialize components
        self.setup_ui()
        self.setup_speech_recognition()
        
    def setup_ui(self):
        """Set up the user interface"""
        # Create document manager (left sidebar)
        self.doc_manager = DocumentManager(self.root)
        self.doc_manager.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Create rich text editor (main area)
        self.editor = RichTextEditor(self.root)
        self.editor.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create menu
        self.create_menu()
        
    def create_toolbar(self):
        """Create the formatting toolbar"""
        toolbar = ttk.Frame(self.root)
        toolbar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=2)
        
        # Add toolbar buttons
        ttk.Button(toolbar, text="New", command=self.editor.new_document).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Open", command=self.doc_manager.open_document).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Save", command=self.editor.save_document).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        # Add formatting controls
        self.create_formatting_controls(toolbar)
        
    def create_formatting_controls(self, toolbar):
        """Create formatting controls in the toolbar"""
        # Font family
        fonts = ["Arial", "Times New Roman", "Courier New", "Helvetica"]
        self.font_family = ttk.Combobox(toolbar, values=fonts, width=15)
        self.font_family.set("Arial")
        self.font_family.pack(side=tk.LEFT, padx=2)
        self.font_family.bind("<<ComboboxSelected>>", self.editor.apply_font)
        
        # Font size
        sizes = [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 36]
        self.font_size = ttk.Combobox(toolbar, values=sizes, width=5)
        self.font_size.set(12)
        self.font_size.pack(side=tk.LEFT, padx=2)
        self.font_size.bind("<<ComboboxSelected>>", self.editor.apply_font)
        
        # Style buttons
        ttk.Button(toolbar, text="B", width=3, command=self.editor.toggle_bold).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="I", width=3, command=self.editor.toggle_italic).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="U", width=3, command=self.editor.toggle_underline).pack(side=tk.LEFT, padx=2)
        
    def create_menu(self):
        """Create the application menu"""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.editor.new_document)
        file_menu.add_command(label="Open", command=self.doc_manager.open_document)
        file_menu.add_command(label="Save", command=self.editor.save_document)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Cut", command=lambda: self.editor.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", command=lambda: self.editor.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", command=lambda: self.editor.event_generate("<<Paste>>"))
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Start Dictation", command=self.start_dictation)
        tools_menu.add_command(label="Stop Dictation", command=self.stop_dictation)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        self.root.config(menu=menubar)
        
    def setup_speech_recognition(self):
        """Set up speech recognition"""
        self.recognizer = SpeechRecognizer()
        self._is_dictating = False
        
    def start_dictation(self):
        """Start speech-to-text dictation"""
        if not self._is_dictating:
            self._is_dictating = True
            self.recognizer.start_listening(self.on_transcription)
            self.logger.info("Started dictation")
            
    def stop_dictation(self):
        """Stop speech-to-text dictation"""
        if self._is_dictating:
            self._is_dictating = False
            self.recognizer.stop_listening()
            self.logger.info("Stopped dictation")
            
    def on_transcription(self, text: str):
        """Handle transcribed text"""
        if text and self._is_dictating:
            self.editor.insert_text(text + " ")
            self.logger.info(f"Inserted text: {text}")
            
    def quit(self):
        """Quit the application"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.stop_dictation()
            self.root.quit()
            
    def run(self):
        """Run the application"""
        try:
            self.logger.info("Starting Mumble Notes")
            self.root.mainloop()
        except KeyboardInterrupt:
            self.logger.info("Shutting down Mumble Notes")
        finally:
            self.stop_dictation()
            
if __name__ == '__main__':
    app = MumbleNotes()
    app.run() 