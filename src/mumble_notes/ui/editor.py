"""
Rich text editor component for Mumble Notes
"""

import tkinter as tk
from tkinter import ttk, font, messagebox
import logging

class RichTextEditor(ttk.Frame):
    """Rich text editor with formatting capabilities"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.logger = logging.getLogger('mumble.notes.editor')
        
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create text widget with scrollbar
        self.create_text_widget()
        
        # Initialize formatting tags
        self.setup_tags()
        
        # Track current font settings
        self.current_font = {
            'family': 'Arial',
            'size': 12,
            'bold': False,
            'italic': False,
            'underline': False
        }
        
    def create_text_widget(self):
        """Create the main text widget and scrollbar"""
        # Create text widget
        self.text = tk.Text(
            self,
            wrap=tk.WORD,
            undo=True,
            font=('Arial', 12)
        )
        
        # Create scrollbar
        scrollbar = ttk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self.text.yview
        )
        
        # Configure text widget scrolling
        self.text.configure(yscrollcommand=scrollbar.set)
        
        # Grid widgets
        self.text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
    def setup_tags(self):
        """Set up text formatting tags"""
        # Base font configurations
        self.text.tag_configure('bold', font=('Arial', 12, 'bold'))
        self.text.tag_configure('italic', font=('Arial', 12, 'italic'))
        self.text.tag_configure('underline', underline=True)
        
    def apply_font(self, event=None):
        """Apply font changes to selected text or cursor position"""
        try:
            # Get font settings from parent
            family = self.master.font_family.get()
            size = int(self.master.font_size.get())
            
            # Update current font
            self.current_font['family'] = family
            self.current_font['size'] = size
            
            # Create font string
            font_str = (family, size)
            if self.current_font['bold']:
                font_str += ('bold',)
            if self.current_font['italic']:
                font_str += ('italic',)
                
            # Apply to selection or insert point
            if self.text.tag_ranges(tk.SEL):
                self.text.tag_add('custom', tk.SEL_FIRST, tk.SEL_LAST)
            else:
                self.text.tag_add('custom', tk.INSERT)
                
            # Configure the custom tag with new font
            self.text.tag_configure('custom', font=font_str)
            
            self.logger.debug(f"Applied font: {font_str}")
            
        except Exception as e:
            self.logger.error(f"Error applying font: {e}")
            messagebox.showerror("Error", "Could not apply font formatting")
            
    def toggle_bold(self):
        """Toggle bold formatting"""
        self.current_font['bold'] = not self.current_font['bold']
        self.apply_font()
        
    def toggle_italic(self):
        """Toggle italic formatting"""
        self.current_font['italic'] = not self.current_font['italic']
        self.apply_font()
        
    def toggle_underline(self):
        """Toggle underline formatting"""
        self.current_font['underline'] = not self.current_font['underline']
        if self.text.tag_ranges(tk.SEL):
            start, end = self.text.tag_ranges(tk.SEL)
            if self.current_font['underline']:
                self.text.tag_add('underline', start, end)
            else:
                self.text.tag_remove('underline', start, end)
                
    def insert_text(self, text: str):
        """Insert text at current cursor position"""
        try:
            self.text.insert(tk.INSERT, text)
            self.logger.debug(f"Inserted text at cursor: {text[:50]}...")
        except Exception as e:
            self.logger.error(f"Error inserting text: {e}")
            
    def new_document(self):
        """Create a new document"""
        if messagebox.askyesno("New Document", "Clear current document?"):
            self.text.delete(1.0, tk.END)
            self.logger.info("Created new document")
            
    def save_document(self):
        """Save the current document"""
        # This is a placeholder - will be implemented with document management
        messagebox.showinfo("Save", "Save functionality coming soon!")
        self.logger.info("Save document requested (not implemented)") 