"""
Tests for the rich text editor component
"""

import pytest
import tkinter as tk
from tkinter import ttk, font
from unittest.mock import MagicMock, patch
import logging

from ..ui.editor import RichTextEditor

@pytest.fixture
def root():
    """Create root window"""
    root = tk.Tk()
    yield root
    root.destroy()

@pytest.fixture
def editor(root):
    """Create RichTextEditor instance"""
    editor = RichTextEditor(root)
    return editor

def test_initialization(editor):
    """Test editor initialization"""
    # Test frame configuration
    assert editor.grid_info()['row'] == 0
    assert editor.grid_info()['column'] == 0
    
    # Test text widget setup
    assert isinstance(editor.text, tk.Text)
    assert editor.text.cget('wrap') == 'word'
    assert editor.text.cget('undo') == '1'
    assert isinstance(editor.text.cget('font'), str)
    
    # Test scrollbar setup
    scrollbar = None
    for child in editor.winfo_children():
        if isinstance(child, ttk.Scrollbar):
            scrollbar = child
            break
    assert scrollbar is not None
    assert scrollbar.cget('orient') == 'vertical'
    
    # Test initial font settings
    assert editor.current_font == {
        'family': 'Arial',
        'size': 12,
        'bold': False,
        'italic': False,
        'underline': False
    }

def test_text_tags(editor):
    """Test text formatting tags"""
    # Test bold tag
    bold_font = editor.text.tag_cget('bold', 'font')
    assert isinstance(bold_font, str)
    assert 'bold' in bold_font
    
    # Test italic tag
    italic_font = editor.text.tag_cget('italic', 'font')
    assert isinstance(italic_font, str)
    assert 'italic' in italic_font
    
    # Test underline tag
    assert editor.text.tag_cget('underline', 'underline') == '1'

def test_font_application(editor):
    """Test applying font changes"""
    # Mock parent widget's font settings
    editor.master.font_family = MagicMock()
    editor.master.font_size = MagicMock()
    editor.master.font_family.get.return_value = 'Times New Roman'
    editor.master.font_size.get.return_value = '14'
    
    # Insert some text
    editor.text.insert('1.0', 'Test text')
    editor.text.tag_add('sel', '1.0', '1.4')  # Select 'Test'
    
    # Apply font changes
    editor.apply_font()
    
    # Verify font changes
    assert editor.current_font['family'] == 'Times New Roman'
    assert editor.current_font['size'] == 14
    
    # Check custom tag
    custom_font = editor.text.tag_cget('custom', 'font')
    assert isinstance(custom_font, str)
    assert 'Times New Roman' in custom_font
    assert '14' in custom_font

def test_bold_toggle(editor):
    """Test bold formatting toggle"""
    # Insert text and select it
    editor.text.insert('1.0', 'Test text')
    editor.text.tag_add('sel', '1.0', '1.4')
    
    # Toggle bold on
    editor.toggle_bold()
    assert editor.current_font['bold']
    
    # Verify bold tag
    tags = editor.text.tag_names('1.0')
    assert 'custom' in tags
    custom_font = editor.text.tag_cget('custom', 'font')
    assert 'bold' in custom_font
    
    # Toggle bold off
    editor.toggle_bold()
    assert not editor.current_font['bold']

def test_italic_toggle(editor):
    """Test italic formatting toggle"""
    # Insert text and select it
    editor.text.insert('1.0', 'Test text')
    editor.text.tag_add('sel', '1.0', '1.4')
    
    # Toggle italic on
    editor.toggle_italic()
    assert editor.current_font['italic']
    
    # Verify italic tag
    tags = editor.text.tag_names('1.0')
    assert 'custom' in tags
    custom_font = editor.text.tag_cget('custom', 'font')
    assert 'italic' in custom_font
    
    # Toggle italic off
    editor.toggle_italic()
    assert not editor.current_font['italic']

def test_underline_toggle(editor):
    """Test underline formatting toggle"""
    # Insert text and select it
    editor.text.insert('1.0', 'Test text')
    editor.text.tag_add('sel', '1.0', '1.4')
    
    # Toggle underline on
    editor.toggle_underline()
    assert editor.current_font['underline']
    
    # Verify underline tag
    tags = editor.text.tag_names('1.0')
    assert 'underline' in tags
    
    # Toggle underline off
    editor.toggle_underline()
    assert not editor.current_font['underline']
    assert 'underline' not in editor.text.tag_names('1.0')

def test_text_insertion(editor):
    """Test text insertion"""
    # Test normal insertion
    editor.insert_text("Hello, world!")
    assert editor.text.get('1.0', 'end-1c') == "Hello, world!"
    
    # Test insertion with formatting
    editor.current_font['bold'] = True
    editor.insert_text(" Bold text")
    assert editor.text.get('1.0', 'end-1c') == "Hello, world! Bold text"
    
    # Verify formatting tags
    tags = editor.text.tag_names('end-1c')
    assert 'custom' in tags

def test_new_document(editor):
    """Test new document creation"""
    # Insert some text
    editor.text.insert('1.0', 'Existing content')
    
    # Mock messagebox.askyesno to return True
    with patch('tkinter.messagebox.askyesno', return_value=True):
        editor.new_document()
        assert editor.text.get('1.0', 'end-1c') == ""
    
    # Mock messagebox.askyesno to return False
    editor.text.insert('1.0', 'Content to keep')
    with patch('tkinter.messagebox.askyesno', return_value=False):
        editor.new_document()
        assert editor.text.get('1.0', 'end-1c') == "Content to keep"

def test_error_handling(editor):
    """Test error handling"""
    # Test font application error
    editor.master.font_size = MagicMock()
    editor.master.font_size.get.side_effect = ValueError
    
    with patch('tkinter.messagebox.showerror') as mock_error:
        editor.apply_font()
        mock_error.assert_called_once()
    
    # Test text insertion error
    editor.text.insert = MagicMock(side_effect=Exception("Insert error"))
    with patch('tkinter.messagebox.showerror') as mock_error:
        editor.insert_text("Test")
        mock_error.assert_called_once()

def test_undo_redo(editor):
    """Test undo/redo functionality"""
    # Insert some text
    editor.insert_text("First line\n")
    editor.insert_text("Second line\n")
    editor.insert_text("Third line")
    
    # Undo last insertion
    editor.text.edit_undo()
    assert editor.text.get('1.0', 'end-1c') == "First line\nSecond line\n"
    
    # Redo last insertion
    editor.text.edit_redo()
    assert editor.text.get('1.0', 'end-1c') == "First line\nSecond line\nThird line"

def test_multiple_selections(editor):
    """Test handling multiple text selections"""
    # Insert text
    editor.text.insert('1.0', 'Test multiple selections')
    
    # Create multiple selections (if supported by tk version)
    try:
        editor.text.tag_add('sel', '1.0', '1.4')  # Select 'Test'
        editor.text.tag_add('sel', '1.13', '1.22')  # Select 'selections'
        
        # Apply formatting
        editor.toggle_bold()
        
        # Verify both selections are formatted
        assert 'custom' in editor.text.tag_names('1.0')
        assert 'custom' in editor.text.tag_names('1.13')
    except tk.TclError:
        # Multiple selections not supported
        pass

def test_performance(editor):
    """Test editor performance with large text"""
    # Insert large amount of text
    large_text = "Test line\n" * 1000
    start_time = editor.text.tk.call('clock', 'milliseconds')
    editor.insert_text(large_text)
    end_time = editor.text.tk.call('clock', 'milliseconds')
    
    # Verify insertion time is reasonable
    assert end_time - start_time < 1000  # Should take less than 1 second

def test_memory_management(editor):
    """Test memory management with text operations"""
    initial_tags = len(editor.text.tag_names())
    
    # Perform multiple formatting operations
    for _ in range(100):
        editor.insert_text("Test")
        editor.toggle_bold()
        editor.toggle_italic()
        editor.toggle_underline()
        editor.text.delete('1.0', 'end')
    
    # Verify no tag leaks
    final_tags = len(editor.text.tag_names())
    assert final_tags <= initial_tags + 3  # Allow for bold, italic, underline tags 