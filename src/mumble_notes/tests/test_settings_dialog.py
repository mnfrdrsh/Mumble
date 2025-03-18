"""
Tests for Mumble Notes settings dialog
"""

import pytest
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from unittest.mock import MagicMock, patch

from ..config.notes_config import NotesConfig
from ..ui.settings_dialog import SettingsDialog

@pytest.fixture
def root():
    """Create root window"""
    root = tk.Tk()
    yield root
    root.destroy()

@pytest.fixture
def temp_config_dir(tmp_path) -> Path:
    """Create temporary config directory"""
    return tmp_path / "config"

@pytest.fixture
def notes_config(temp_config_dir) -> NotesConfig:
    """Create NotesConfig instance with temporary directory"""
    config = NotesConfig()
    config.handler.config_dir = temp_config_dir
    config.handler.config_file = temp_config_dir / "notes_config.json"
    config.handler.save_config()
    return config

@pytest.fixture
def dialog(root, notes_config):
    """Create settings dialog"""
    dialog = SettingsDialog(root, notes_config)
    return dialog

def test_dialog_initialization(dialog):
    """Test dialog initialization"""
    assert dialog.title() == "Mumble Notes Settings"
    assert isinstance(dialog.notebook, ttk.Notebook)
    assert len(dialog.notebook.tabs()) == 4  # Editor, Theme, Documents, Speech

def test_editor_tab_widgets(dialog):
    """Test editor tab widgets"""
    # Font settings
    assert isinstance(dialog.font_family, ttk.Combobox)
    assert isinstance(dialog.font_size, ttk.Spinbox)
    assert isinstance(dialog.line_spacing, ttk.Spinbox)
    assert isinstance(dialog.tab_size, ttk.Spinbox)
    
    # Checkboxes
    assert isinstance(dialog.wrap_text, tk.BooleanVar)
    assert isinstance(dialog.show_line_numbers, tk.BooleanVar)
    assert isinstance(dialog.auto_save, tk.BooleanVar)
    assert isinstance(dialog.auto_save_interval, ttk.Spinbox)

def test_theme_tab_widgets(dialog):
    """Test theme tab widgets"""
    assert isinstance(dialog.theme_name, ttk.Combobox)
    assert isinstance(dialog.bg_color, tk.StringVar)
    assert isinstance(dialog.text_color, tk.StringVar)
    assert isinstance(dialog.accent_color, tk.StringVar)
    assert isinstance(dialog.sidebar_width, ttk.Spinbox)

def test_documents_tab_widgets(dialog):
    """Test documents tab widgets"""
    assert isinstance(dialog.default_format, ttk.Combobox)
    assert isinstance(dialog.backup_enabled, tk.BooleanVar)
    assert isinstance(dialog.backup_count, ttk.Spinbox)
    assert isinstance(dialog.categories_list, tk.Listbox)

def test_speech_tab_widgets(dialog):
    """Test speech tab widgets"""
    assert isinstance(dialog.language, ttk.Combobox)
    assert isinstance(dialog.ambient_duration, ttk.Spinbox)
    assert isinstance(dialog.auto_punctuate, tk.BooleanVar)
    assert isinstance(dialog.capitalize_sentences, tk.BooleanVar)

def test_load_settings(dialog, notes_config):
    """Test loading settings into UI"""
    # Editor settings
    assert dialog.font_family.get() == notes_config.editor_settings['font_family']
    assert int(dialog.font_size.get()) == notes_config.editor_settings['font_size']
    assert float(dialog.line_spacing.get()) == notes_config.editor_settings['line_spacing']
    assert int(dialog.tab_size.get()) == notes_config.editor_settings['tab_size']
    assert dialog.wrap_text.get() == notes_config.editor_settings['wrap_text']
    assert dialog.show_line_numbers.get() == notes_config.editor_settings['show_line_numbers']
    assert dialog.auto_save.get() == notes_config.editor_settings['auto_save']
    assert int(dialog.auto_save_interval.get()) == notes_config.editor_settings['auto_save_interval']
    
    # Theme settings
    assert dialog.theme_name.get() == notes_config.theme_settings['name']
    assert dialog.bg_color.get() == notes_config.theme_settings['background_color']
    assert dialog.text_color.get() == notes_config.theme_settings['text_color']
    assert dialog.accent_color.get() == notes_config.theme_settings['accent_color']
    assert int(dialog.sidebar_width.get()) == notes_config.theme_settings['sidebar_width']
    
    # Document settings
    assert dialog.default_format.get() == notes_config.document_settings['default_format']
    assert dialog.backup_enabled.get() == notes_config.document_settings['backup_enabled']
    assert int(dialog.backup_count.get()) == notes_config.document_settings['backup_count']
    categories = list(dialog.categories_list.get(0, tk.END))
    assert categories == notes_config.document_settings['categories']
    
    # Speech settings
    assert dialog.language.get() == notes_config.speech_settings['language']
    assert float(dialog.ambient_duration.get()) == notes_config.speech_settings['ambient_duration']
    assert dialog.auto_punctuate.get() == notes_config.speech_settings['auto_punctuate']
    assert dialog.capitalize_sentences.get() == notes_config.speech_settings['capitalize_sentences']

def test_apply_settings(dialog, notes_config):
    """Test applying settings from UI"""
    # Modify UI values
    dialog.font_family.set('Courier New')
    dialog.font_size.set('14')
    dialog.line_spacing.set('1.5')
    dialog.tab_size.set('2')
    dialog.wrap_text.set(False)
    dialog.show_line_numbers.set(True)
    dialog.auto_save.set(False)
    dialog.auto_save_interval.set('600')
    
    dialog.theme_name.set('dark')
    dialog.bg_color.set('#000000')
    dialog.text_color.set('#FFFFFF')
    dialog.accent_color.set('#FF0000')
    dialog.sidebar_width.set('300')
    
    dialog.default_format.set('md')
    dialog.backup_enabled.set(False)
    dialog.backup_count.set('3')
    dialog.categories_list.delete(0, tk.END)
    dialog.categories_list.insert(tk.END, 'Test')
    
    dialog.language.set('en-GB')
    dialog.ambient_duration.set('1.0')
    dialog.auto_punctuate.set(False)
    dialog.capitalize_sentences.set(False)
    
    # Apply settings
    dialog._apply_settings()
    
    # Verify config values
    editor = notes_config.editor_settings
    assert editor['font_family'] == 'Courier New'
    assert editor['font_size'] == 14
    assert editor['line_spacing'] == 1.5
    assert editor['tab_size'] == 2
    assert editor['wrap_text'] is False
    assert editor['show_line_numbers'] is True
    assert editor['auto_save'] is False
    assert editor['auto_save_interval'] == 600
    
    theme = notes_config.theme_settings
    assert theme['name'] == 'dark'
    assert theme['background_color'] == '#000000'
    assert theme['text_color'] == '#FFFFFF'
    assert theme['accent_color'] == '#FF0000'
    assert theme['sidebar_width'] == 300
    
    docs = notes_config.document_settings
    assert docs['default_format'] == 'md'
    assert docs['backup_enabled'] is False
    assert docs['backup_count'] == 3
    assert docs['categories'] == ['Test']
    
    speech = notes_config.speech_settings
    assert speech['language'] == 'en-GB'
    assert speech['ambient_duration'] == 1.0
    assert speech['auto_punctuate'] is False
    assert speech['capitalize_sentences'] is False

def test_reset_defaults(dialog, notes_config):
    """Test resetting settings to defaults"""
    # Modify settings
    dialog.font_family.set('Courier New')
    dialog.theme_name.set('dark')
    dialog.default_format.set('md')
    dialog.language.set('en-GB')
    
    # Mock messagebox.askyesno to return True
    with patch('tkinter.messagebox.askyesno', return_value=True):
        dialog._reset_defaults()
    
    # Verify UI values are reset
    assert dialog.font_family.get() == notes_config.editor_settings['font_family']
    assert dialog.theme_name.get() == notes_config.theme_settings['name']
    assert dialog.default_format.get() == notes_config.document_settings['default_format']
    assert dialog.language.get() == notes_config.speech_settings['language']

def test_add_category(dialog):
    """Test adding document category"""
    # Create mock Toplevel dialog
    mock_dialog = MagicMock()
    mock_entry = MagicMock()
    mock_entry.get.return_value = "Test Category"
    
    with patch('tkinter.Toplevel', return_value=mock_dialog):
        with patch('tkinter.ttk.Entry', return_value=mock_entry):
            dialog._add_category()
            
            # Simulate clicking Add button
            mock_dialog.destroy.side_effect = lambda: dialog.categories_list.insert(tk.END, mock_entry.get())
            for child in mock_dialog.children.values():
                if isinstance(child, ttk.Button) and child['text'] == 'Add':
                    child.invoke()
    
    # Verify category was added
    categories = list(dialog.categories_list.get(0, tk.END))
    assert "Test Category" in categories

def test_remove_category(dialog):
    """Test removing document category"""
    # Add test category
    dialog.categories_list.insert(tk.END, "Test Category")
    
    # Select and remove category
    dialog.categories_list.selection_set(0)
    dialog._remove_category()
    
    # Verify category was removed
    categories = list(dialog.categories_list.get(0, tk.END))
    assert "Test Category" not in categories

def test_color_picker(dialog):
    """Test color picker dialog"""
    color_var = tk.StringVar(value='#000000')
    
    # Mock colorchooser.askcolor to return a color
    with patch('tkinter.colorchooser.askcolor', return_value=('#FFFFFF', '#FFFFFF')):
        dialog._pick_color(color_var)
        assert color_var.get() == '#FFFFFF'
    
    # Mock colorchooser.askcolor to return None (dialog cancelled)
    with patch('tkinter.colorchooser.askcolor', return_value=(None, None)):
        dialog._pick_color(color_var)
        assert color_var.get() == '#FFFFFF'  # Value should not change 