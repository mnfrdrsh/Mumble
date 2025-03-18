"""
Settings dialog for Mumble Notes
"""

import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from typing import Dict, Any, Callable
import logging

from ..config.notes_config import NotesConfig

logger = logging.getLogger('mumble.notes.settings')

class SettingsDialog(tk.Toplevel):
    """Settings dialog with tabbed interface"""
    
    def __init__(self, parent: tk.Widget, config: NotesConfig):
        """Initialize settings dialog"""
        super().__init__(parent)
        self.parent = parent
        self.config = config
        
        self.title("Mumble Notes Settings")
        self.geometry("600x500")
        self.resizable(True, True)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Initialize UI
        self._create_widgets()
        self._load_settings()
        
        # Center dialog
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def _create_widgets(self) -> None:
        """Create dialog widgets"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Create tabs
        self.editor_tab = self._create_editor_tab()
        self.theme_tab = self._create_theme_tab()
        self.documents_tab = self._create_documents_tab()
        self.speech_tab = self._create_speech_tab()
        
        # Add tabs to notebook
        self.notebook.add(self.editor_tab, text="Editor")
        self.notebook.add(self.theme_tab, text="Theme")
        self.notebook.add(self.documents_tab, text="Documents")
        self.notebook.add(self.speech_tab, text="Speech")
        
        # Create bottom buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(button_frame, text="Apply", command=self._apply_settings).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Reset to Defaults", command=self._reset_defaults).pack(side='left', padx=5)
        
    def _create_editor_tab(self) -> ttk.Frame:
        """Create editor settings tab"""
        tab = ttk.Frame(self.notebook)
        tab.columnconfigure(1, weight=1)
        
        # Font settings
        row = 0
        ttk.Label(tab, text="Font Family:").grid(row=row, column=0, sticky='w', padx=5, pady=5)
        self.font_family = ttk.Combobox(tab, values=['Arial', 'Times New Roman', 'Courier New'])
        self.font_family.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        
        row += 1
        ttk.Label(tab, text="Font Size:").grid(row=row, column=0, sticky='w', padx=5, pady=5)
        self.font_size = ttk.Spinbox(tab, from_=8, to=72)
        self.font_size.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        
        row += 1
        ttk.Label(tab, text="Line Spacing:").grid(row=row, column=0, sticky='w', padx=5, pady=5)
        self.line_spacing = ttk.Spinbox(tab, from_=1.0, to=3.0, increment=0.1)
        self.line_spacing.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        
        row += 1
        ttk.Label(tab, text="Tab Size:").grid(row=row, column=0, sticky='w', padx=5, pady=5)
        self.tab_size = ttk.Spinbox(tab, from_=2, to=8)
        self.tab_size.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        
        # Checkboxes
        row += 1
        self.wrap_text = tk.BooleanVar()
        ttk.Checkbutton(tab, text="Wrap Text", variable=self.wrap_text).grid(row=row, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        
        row += 1
        self.show_line_numbers = tk.BooleanVar()
        ttk.Checkbutton(tab, text="Show Line Numbers", variable=self.show_line_numbers).grid(row=row, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        
        row += 1
        self.auto_save = tk.BooleanVar()
        ttk.Checkbutton(tab, text="Auto Save", variable=self.auto_save).grid(row=row, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        
        row += 1
        ttk.Label(tab, text="Auto Save Interval (seconds):").grid(row=row, column=0, sticky='w', padx=5, pady=5)
        self.auto_save_interval = ttk.Spinbox(tab, from_=30, to=3600)
        self.auto_save_interval.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        
        return tab
        
    def _create_theme_tab(self) -> ttk.Frame:
        """Create theme settings tab"""
        tab = ttk.Frame(self.notebook)
        tab.columnconfigure(1, weight=1)
        
        row = 0
        ttk.Label(tab, text="Theme:").grid(row=row, column=0, sticky='w', padx=5, pady=5)
        self.theme_name = ttk.Combobox(tab, values=['clam', 'alt', 'default', 'classic'])
        self.theme_name.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        
        # Color pickers
        row += 1
        ttk.Label(tab, text="Background Color:").grid(row=row, column=0, sticky='w', padx=5, pady=5)
        self.bg_color_frame = ttk.Frame(tab)
        self.bg_color_frame.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        self.bg_color = tk.StringVar()
        ttk.Entry(self.bg_color_frame, textvariable=self.bg_color).pack(side='left', expand=True, fill='x')
        ttk.Button(self.bg_color_frame, text="Pick", command=lambda: self._pick_color(self.bg_color)).pack(side='right', padx=5)
        
        row += 1
        ttk.Label(tab, text="Text Color:").grid(row=row, column=0, sticky='w', padx=5, pady=5)
        self.text_color_frame = ttk.Frame(tab)
        self.text_color_frame.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        self.text_color = tk.StringVar()
        ttk.Entry(self.text_color_frame, textvariable=self.text_color).pack(side='left', expand=True, fill='x')
        ttk.Button(self.text_color_frame, text="Pick", command=lambda: self._pick_color(self.text_color)).pack(side='right', padx=5)
        
        row += 1
        ttk.Label(tab, text="Accent Color:").grid(row=row, column=0, sticky='w', padx=5, pady=5)
        self.accent_color_frame = ttk.Frame(tab)
        self.accent_color_frame.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        self.accent_color = tk.StringVar()
        ttk.Entry(self.accent_color_frame, textvariable=self.accent_color).pack(side='left', expand=True, fill='x')
        ttk.Button(self.accent_color_frame, text="Pick", command=lambda: self._pick_color(self.accent_color)).pack(side='right', padx=5)
        
        row += 1
        ttk.Label(tab, text="Sidebar Width:").grid(row=row, column=0, sticky='w', padx=5, pady=5)
        self.sidebar_width = ttk.Spinbox(tab, from_=150, to=500)
        self.sidebar_width.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        
        return tab
        
    def _create_documents_tab(self) -> ttk.Frame:
        """Create documents settings tab"""
        tab = ttk.Frame(self.notebook)
        tab.columnconfigure(1, weight=1)
        
        row = 0
        ttk.Label(tab, text="Default Format:").grid(row=row, column=0, sticky='w', padx=5, pady=5)
        self.default_format = ttk.Combobox(tab, values=['rtf', 'txt', 'md'])
        self.default_format.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        
        row += 1
        self.backup_enabled = tk.BooleanVar()
        ttk.Checkbutton(tab, text="Enable Backups", variable=self.backup_enabled).grid(row=row, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        
        row += 1
        ttk.Label(tab, text="Backup Count:").grid(row=row, column=0, sticky='w', padx=5, pady=5)
        self.backup_count = ttk.Spinbox(tab, from_=1, to=10)
        self.backup_count.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        
        # Categories
        row += 1
        ttk.Label(tab, text="Categories:").grid(row=row, column=0, sticky='w', padx=5, pady=5)
        
        categories_frame = ttk.Frame(tab)
        categories_frame.grid(row=row, column=1, sticky='nsew', padx=5, pady=5)
        categories_frame.columnconfigure(0, weight=1)
        
        self.categories_list = tk.Listbox(categories_frame, height=5)
        self.categories_list.grid(row=0, column=0, sticky='nsew')
        
        scrollbar = ttk.Scrollbar(categories_frame, orient='vertical', command=self.categories_list.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.categories_list.configure(yscrollcommand=scrollbar.set)
        
        buttons_frame = ttk.Frame(categories_frame)
        buttons_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=5)
        
        ttk.Button(buttons_frame, text="Add", command=self._add_category).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Remove", command=self._remove_category).pack(side='left', padx=5)
        
        return tab
        
    def _create_speech_tab(self) -> ttk.Frame:
        """Create speech settings tab"""
        tab = ttk.Frame(self.notebook)
        tab.columnconfigure(1, weight=1)
        
        row = 0
        ttk.Label(tab, text="Language:").grid(row=row, column=0, sticky='w', padx=5, pady=5)
        self.language = ttk.Combobox(tab, values=['en-US', 'en-GB', 'es-ES', 'fr-FR', 'de-DE'])
        self.language.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        
        row += 1
        ttk.Label(tab, text="Ambient Duration (seconds):").grid(row=row, column=0, sticky='w', padx=5, pady=5)
        self.ambient_duration = ttk.Spinbox(tab, from_=0.1, to=2.0, increment=0.1)
        self.ambient_duration.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        
        row += 1
        self.auto_punctuate = tk.BooleanVar()
        ttk.Checkbutton(tab, text="Auto Punctuate", variable=self.auto_punctuate).grid(row=row, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        
        row += 1
        self.capitalize_sentences = tk.BooleanVar()
        ttk.Checkbutton(tab, text="Capitalize Sentences", variable=self.capitalize_sentences).grid(row=row, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        
        return tab
        
    def _load_settings(self) -> None:
        """Load current settings into UI"""
        # Editor settings
        editor = self.config.editor_settings
        self.font_family.set(editor['font_family'])
        self.font_size.set(editor['font_size'])
        self.line_spacing.set(editor['line_spacing'])
        self.tab_size.set(editor['tab_size'])
        self.wrap_text.set(editor['wrap_text'])
        self.show_line_numbers.set(editor['show_line_numbers'])
        self.auto_save.set(editor['auto_save'])
        self.auto_save_interval.set(editor['auto_save_interval'])
        
        # Theme settings
        theme = self.config.theme_settings
        self.theme_name.set(theme['name'])
        self.bg_color.set(theme['background_color'])
        self.text_color.set(theme['text_color'])
        self.accent_color.set(theme['accent_color'])
        self.sidebar_width.set(theme['sidebar_width'])
        
        # Document settings
        docs = self.config.document_settings
        self.default_format.set(docs['default_format'])
        self.backup_enabled.set(docs['backup_enabled'])
        self.backup_count.set(docs['backup_count'])
        
        self.categories_list.delete(0, tk.END)
        for category in docs['categories']:
            self.categories_list.insert(tk.END, category)
            
        # Speech settings
        speech = self.config.speech_settings
        self.language.set(speech['language'])
        self.ambient_duration.set(speech['ambient_duration'])
        self.auto_punctuate.set(speech['auto_punctuate'])
        self.capitalize_sentences.set(speech['capitalize_sentences'])
        
    def _apply_settings(self) -> None:
        """Apply settings from UI to config"""
        try:
            # Editor settings
            self.config.update_editor_settings({
                'font_family': self.font_family.get(),
                'font_size': int(self.font_size.get()),
                'line_spacing': float(self.line_spacing.get()),
                'tab_size': int(self.tab_size.get()),
                'wrap_text': self.wrap_text.get(),
                'show_line_numbers': self.show_line_numbers.get(),
                'auto_save': self.auto_save.get(),
                'auto_save_interval': int(self.auto_save_interval.get())
            })
            
            # Theme settings
            self.config.update_theme_settings({
                'name': self.theme_name.get(),
                'background_color': self.bg_color.get(),
                'text_color': self.text_color.get(),
                'accent_color': self.accent_color.get(),
                'sidebar_width': int(self.sidebar_width.get())
            })
            
            # Document settings
            self.config.update_document_settings({
                'default_format': self.default_format.get(),
                'backup_enabled': self.backup_enabled.get(),
                'backup_count': int(self.backup_count.get()),
                'categories': list(self.categories_list.get(0, tk.END))
            })
            
            # Speech settings
            self.config.update_speech_settings({
                'language': self.language.get(),
                'ambient_duration': float(self.ambient_duration.get()),
                'auto_punctuate': self.auto_punctuate.get(),
                'capitalize_sentences': self.capitalize_sentences.get()
            })
            
            logger.info("Settings applied successfully")
            self.destroy()
            
        except Exception as e:
            logger.error(f"Error applying settings: {e}")
            messagebox.showerror("Error", f"Failed to apply settings: {str(e)}")
            
    def _reset_defaults(self) -> None:
        """Reset all settings to defaults"""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            self.config.reset_to_defaults()
            self._load_settings()
            logger.info("Settings reset to defaults")
            
    def _pick_color(self, color_var: tk.StringVar) -> None:
        """Open color picker dialog"""
        color = colorchooser.askcolor(color_var.get())
        if color[1]:
            color_var.set(color[1])
            
    def _add_category(self) -> None:
        """Add new category"""
        dialog = tk.Toplevel(self)
        dialog.title("Add Category")
        dialog.transient(self)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Category Name:").pack(padx=5, pady=5)
        entry = ttk.Entry(dialog)
        entry.pack(padx=5, pady=5)
        
        def add():
            name = entry.get().strip()
            if name:
                self.categories_list.insert(tk.END, name)
                dialog.destroy()
                
        ttk.Button(dialog, text="Add", command=add).pack(padx=5, pady=5)
        
    def _remove_category(self) -> None:
        """Remove selected category"""
        selection = self.categories_list.curselection()
        if selection:
            self.categories_list.delete(selection) 