"""
Tests for Mumble Notes configuration
"""

import pytest
from pathlib import Path
from typing import Dict, Any

from ..config.notes_config import NotesConfig, DEFAULTS

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

def test_default_values(notes_config):
    """Test default configuration values"""
    # Window settings
    window = notes_config.window_settings
    assert window['width'] == DEFAULTS['window']['width']
    assert window['height'] == DEFAULTS['window']['height']
    assert window['position'] is None
    assert window['maximized'] is False
    
    # Editor settings
    editor = notes_config.editor_settings
    assert editor['font_family'] == DEFAULTS['editor']['font_family']
    assert editor['font_size'] == DEFAULTS['editor']['font_size']
    assert editor['line_spacing'] == DEFAULTS['editor']['line_spacing']
    assert editor['tab_size'] == DEFAULTS['editor']['tab_size']
    assert editor['wrap_text'] == DEFAULTS['editor']['wrap_text']
    assert editor['show_line_numbers'] == DEFAULTS['editor']['show_line_numbers']
    assert editor['auto_save'] == DEFAULTS['editor']['auto_save']
    assert editor['auto_save_interval'] == DEFAULTS['editor']['auto_save_interval']
    
    # Theme settings
    theme = notes_config.theme_settings
    assert theme['name'] == DEFAULTS['theme']['name']
    assert theme['background_color'] == DEFAULTS['theme']['background_color']
    assert theme['text_color'] == DEFAULTS['theme']['text_color']
    assert theme['accent_color'] == DEFAULTS['theme']['accent_color']
    assert theme['sidebar_width'] == DEFAULTS['theme']['sidebar_width']
    
    # Document settings
    docs = notes_config.document_settings
    assert docs['storage_path'] == DEFAULTS['documents']['storage_path']
    assert docs['default_format'] == DEFAULTS['documents']['default_format']
    assert docs['backup_enabled'] == DEFAULTS['documents']['backup_enabled']
    assert docs['backup_count'] == DEFAULTS['documents']['backup_count']
    assert docs['categories'] == DEFAULTS['documents']['categories']
    
    # Speech settings
    speech = notes_config.speech_settings
    assert speech['language'] == DEFAULTS['speech']['language']
    assert speech['ambient_duration'] == DEFAULTS['speech']['ambient_duration']
    assert speech['auto_punctuate'] == DEFAULTS['speech']['auto_punctuate']
    assert speech['capitalize_sentences'] == DEFAULTS['speech']['capitalize_sentences']

def test_update_window_settings(notes_config):
    """Test updating window settings"""
    updates = {
        'width': 1000,
        'height': 600,
        'position': {'x': 100, 'y': 100},
        'maximized': True
    }
    notes_config.update_window_settings(updates)
    
    window = notes_config.window_settings
    assert window['width'] == 1000
    assert window['height'] == 600
    assert window['position'] == {'x': 100, 'y': 100}
    assert window['maximized'] is True

def test_update_editor_settings(notes_config):
    """Test updating editor settings"""
    updates = {
        'font_family': 'Courier New',
        'font_size': 14,
        'line_spacing': 1.5,
        'tab_size': 2,
        'wrap_text': False,
        'show_line_numbers': True,
        'auto_save': False,
        'auto_save_interval': 600
    }
    notes_config.update_editor_settings(updates)
    
    editor = notes_config.editor_settings
    assert editor['font_family'] == 'Courier New'
    assert editor['font_size'] == 14
    assert editor['line_spacing'] == 1.5
    assert editor['tab_size'] == 2
    assert editor['wrap_text'] is False
    assert editor['show_line_numbers'] is True
    assert editor['auto_save'] is False
    assert editor['auto_save_interval'] == 600

def test_update_theme_settings(notes_config):
    """Test updating theme settings"""
    updates = {
        'name': 'dark',
        'background_color': '#000000',
        'text_color': '#FFFFFF',
        'accent_color': '#FF0000',
        'sidebar_width': 300
    }
    notes_config.update_theme_settings(updates)
    
    theme = notes_config.theme_settings
    assert theme['name'] == 'dark'
    assert theme['background_color'] == '#000000'
    assert theme['text_color'] == '#FFFFFF'
    assert theme['accent_color'] == '#FF0000'
    assert theme['sidebar_width'] == 300

def test_update_document_settings(notes_config):
    """Test updating document settings"""
    updates = {
        'storage_path': 'custom_docs',
        'default_format': 'md',
        'backup_enabled': False,
        'backup_count': 3,
        'categories': ['Work', 'Personal', 'Projects']
    }
    notes_config.update_document_settings(updates)
    
    docs = notes_config.document_settings
    assert docs['storage_path'] == 'custom_docs'
    assert docs['default_format'] == 'md'
    assert docs['backup_enabled'] is False
    assert docs['backup_count'] == 3
    assert docs['categories'] == ['Work', 'Personal', 'Projects']

def test_update_speech_settings(notes_config):
    """Test updating speech settings"""
    updates = {
        'language': 'en-GB',
        'ambient_duration': 1.0,
        'auto_punctuate': False,
        'capitalize_sentences': False
    }
    notes_config.update_speech_settings(updates)
    
    speech = notes_config.speech_settings
    assert speech['language'] == 'en-GB'
    assert speech['ambient_duration'] == 1.0
    assert speech['auto_punctuate'] is False
    assert speech['capitalize_sentences'] is False

def test_add_remove_category(notes_config):
    """Test adding and removing document categories"""
    # Add category
    notes_config.add_category('Test')
    assert 'Test' in notes_config.document_settings['categories']
    
    # Add duplicate category
    notes_config.add_category('Test')
    assert notes_config.document_settings['categories'].count('Test') == 1
    
    # Remove category
    notes_config.remove_category('Test')
    assert 'Test' not in notes_config.document_settings['categories']
    
    # Remove nonexistent category
    notes_config.remove_category('Nonexistent')  # Should not raise error

def test_save_window_position(notes_config):
    """Test saving window position"""
    notes_config.save_window_position(100, 200, 800, 600, False)
    
    window = notes_config.window_settings
    assert window['position'] == {'x': 100, 'y': 200}
    assert window['width'] == 800
    assert window['height'] == 600
    assert window['maximized'] is False

def test_documents_path(notes_config, temp_config_dir):
    """Test documents path resolution"""
    # Default path
    expected_path = temp_config_dir / DEFAULTS['documents']['storage_path']
    assert notes_config.documents_path == expected_path
    assert notes_config.documents_path.exists()
    
    # Custom path
    custom_path = 'custom_docs'
    notes_config.update_document_settings({'storage_path': custom_path})
    expected_path = temp_config_dir / custom_path
    assert notes_config.documents_path == expected_path
    assert notes_config.documents_path.exists()

def test_reset_to_defaults(notes_config):
    """Test resetting all settings to defaults"""
    # Modify settings
    notes_config.update_window_settings({'width': 1000, 'height': 600})
    notes_config.update_editor_settings({'font_size': 14, 'auto_save': False})
    notes_config.update_theme_settings({'name': 'dark', 'background_color': '#000000'})
    notes_config.add_category('Test')
    
    # Reset to defaults
    notes_config.reset_to_defaults()
    
    # Verify all settings are back to defaults
    assert notes_config.window_settings == DEFAULTS['window']
    assert notes_config.editor_settings == DEFAULTS['editor']
    assert notes_config.theme_settings == DEFAULTS['theme']
    assert notes_config.document_settings == DEFAULTS['documents']
    assert notes_config.speech_settings == DEFAULTS['speech'] 