"""
Tests for Mumble Quick configuration
"""

import pytest
from pathlib import Path
from typing import Dict, Any

from ..config.quick_config import QuickConfig, DEFAULTS

@pytest.fixture
def temp_config_dir(tmp_path) -> Path:
    """Create temporary config directory"""
    return tmp_path / "config"

@pytest.fixture
def quick_config(temp_config_dir) -> QuickConfig:
    """Create QuickConfig instance with temporary directory"""
    config = QuickConfig()
    config.handler.config_dir = temp_config_dir
    config.handler.config_file = temp_config_dir / "quick_config.json"
    config.handler.save_config()
    return config

def test_default_values(quick_config):
    """Test default configuration values"""
    # Hotkey settings
    hotkey = quick_config.handler.get('hotkey')
    assert hotkey['trigger'] == DEFAULTS['hotkey']['trigger']
    assert hotkey['stop'] == DEFAULTS['hotkey']['stop']
    
    # UI settings
    ui = quick_config.ui_settings
    assert ui['bar_width'] == DEFAULTS['ui']['bar_width']
    assert ui['bar_height'] == DEFAULTS['ui']['bar_height']
    assert ui['background_color'] == DEFAULTS['ui']['background_color']
    assert ui['foreground_color'] == DEFAULTS['ui']['foreground_color']
    assert ui['font_color'] == DEFAULTS['ui']['font_color']
    assert ui['opacity'] == DEFAULTS['ui']['opacity']
    assert ui['animation_speed'] == DEFAULTS['ui']['animation_speed']
    assert ui['show_close_button'] == DEFAULTS['ui']['show_close_button']
    
    # Speech settings
    speech = quick_config.speech_settings
    assert speech['language'] == DEFAULTS['speech']['language']
    assert speech['ambient_duration'] == DEFAULTS['speech']['ambient_duration']
    assert speech['phrase_timeout'] == DEFAULTS['speech']['phrase_timeout']
    assert speech['auto_stop'] == DEFAULTS['speech']['auto_stop']
    assert speech['auto_stop_timeout'] == DEFAULTS['speech']['auto_stop_timeout']
    
    # Tray settings
    tray = quick_config.tray_settings
    assert tray['show_notifications'] == DEFAULTS['tray']['show_notifications']
    assert tray['minimize_to_tray'] == DEFAULTS['tray']['minimize_to_tray']
    assert tray['start_minimized'] == DEFAULTS['tray']['start_minimized']
    
    # Behavior settings
    behavior = quick_config.behavior_settings
    assert behavior['auto_paste'] == DEFAULTS['behavior']['auto_paste']
    assert behavior['add_trailing_space'] == DEFAULTS['behavior']['add_trailing_space']
    assert behavior['capitalize_sentences'] == DEFAULTS['behavior']['capitalize_sentences']
    assert behavior['save_position'] == DEFAULTS['behavior']['save_position']
    assert behavior['last_position'] == DEFAULTS['behavior']['last_position']

def test_hotkey_trigger(quick_config):
    """Test hotkey trigger property"""
    assert quick_config.hotkey_trigger == DEFAULTS['hotkey']['trigger']
    
    quick_config.hotkey_trigger = 'ctrl+shift'
    assert quick_config.hotkey_trigger == 'ctrl+shift'
    assert quick_config.handler.get('hotkey')['trigger'] == 'ctrl+shift'

def test_update_ui_settings(quick_config):
    """Test updating UI settings"""
    updates = {
        'bar_width': 150,
        'bar_height': 30,
        'background_color': '#333333',
        'foreground_color': '#00FF00',
        'font_color': '#CCCCCC',
        'opacity': 0.8,
        'animation_speed': 0.5,
        'show_close_button': False
    }
    quick_config.update_ui_settings(updates)
    
    ui = quick_config.ui_settings
    assert ui['bar_width'] == 150
    assert ui['bar_height'] == 30
    assert ui['background_color'] == '#333333'
    assert ui['foreground_color'] == '#00FF00'
    assert ui['font_color'] == '#CCCCCC'
    assert ui['opacity'] == 0.8
    assert ui['animation_speed'] == 0.5
    assert ui['show_close_button'] is False

def test_update_speech_settings(quick_config):
    """Test updating speech settings"""
    updates = {
        'language': 'en-GB',
        'ambient_duration': 1.0,
        'phrase_timeout': 5.0,
        'auto_stop': False,
        'auto_stop_timeout': 3.0
    }
    quick_config.update_speech_settings(updates)
    
    speech = quick_config.speech_settings
    assert speech['language'] == 'en-GB'
    assert speech['ambient_duration'] == 1.0
    assert speech['phrase_timeout'] == 5.0
    assert speech['auto_stop'] is False
    assert speech['auto_stop_timeout'] == 3.0

def test_update_tray_settings(quick_config):
    """Test updating system tray settings"""
    updates = {
        'show_notifications': False,
        'minimize_to_tray': False,
        'start_minimized': True
    }
    quick_config.update_tray_settings(updates)
    
    tray = quick_config.tray_settings
    assert tray['show_notifications'] is False
    assert tray['minimize_to_tray'] is False
    assert tray['start_minimized'] is True

def test_update_behavior_settings(quick_config):
    """Test updating behavior settings"""
    updates = {
        'auto_paste': False,
        'add_trailing_space': False,
        'capitalize_sentences': False,
        'save_position': False,
        'last_position': {'x': 100, 'y': 100}
    }
    quick_config.update_behavior_settings(updates)
    
    behavior = quick_config.behavior_settings
    assert behavior['auto_paste'] is False
    assert behavior['add_trailing_space'] is False
    assert behavior['capitalize_sentences'] is False
    assert behavior['save_position'] is False
    assert behavior['last_position'] == {'x': 100, 'y': 100}

def test_save_window_position(quick_config):
    """Test saving window position"""
    quick_config.save_window_position(100, 200)
    
    behavior = quick_config.behavior_settings
    assert behavior['last_position'] == {'x': 100, 'y': 200}

def test_reset_to_defaults(quick_config):
    """Test resetting all settings to defaults"""
    # Modify settings
    quick_config.hotkey_trigger = 'ctrl+shift'
    quick_config.update_ui_settings({'bar_width': 150, 'opacity': 0.8})
    quick_config.update_speech_settings({'language': 'en-GB', 'auto_stop': False})
    quick_config.update_tray_settings({'show_notifications': False})
    quick_config.update_behavior_settings({'auto_paste': False})
    quick_config.save_window_position(100, 100)
    
    # Reset to defaults
    quick_config.reset_to_defaults()
    
    # Verify all settings are back to defaults
    assert quick_config.hotkey_trigger == DEFAULTS['hotkey']['trigger']
    assert quick_config.ui_settings == DEFAULTS['ui']
    assert quick_config.speech_settings == DEFAULTS['speech']
    assert quick_config.tray_settings == DEFAULTS['tray']
    assert quick_config.behavior_settings == DEFAULTS['behavior']

def test_persistence(quick_config, temp_config_dir):
    """Test configuration persistence"""
    # Modify settings
    quick_config.hotkey_trigger = 'ctrl+shift'
    quick_config.update_ui_settings({'bar_width': 150})
    quick_config.save_window_position(100, 100)
    
    # Create new instance with same config directory
    new_config = QuickConfig()
    new_config.handler.config_dir = temp_config_dir
    new_config.handler.config_file = temp_config_dir / "quick_config.json"
    
    # Verify settings are loaded from file
    assert new_config.hotkey_trigger == 'ctrl+shift'
    assert new_config.ui_settings['bar_width'] == 150
    assert new_config.behavior_settings['last_position'] == {'x': 100, 'y': 100}

def test_invalid_values(quick_config):
    """Test handling of invalid configuration values"""
    # Invalid bar dimensions
    with pytest.raises(ValueError):
        quick_config.update_ui_settings({'bar_width': -1})
    with pytest.raises(ValueError):
        quick_config.update_ui_settings({'bar_height': 0})
        
    # Invalid opacity
    with pytest.raises(ValueError):
        quick_config.update_ui_settings({'opacity': 2.0})
    with pytest.raises(ValueError):
        quick_config.update_ui_settings({'opacity': -0.1})
        
    # Invalid animation speed
    with pytest.raises(ValueError):
        quick_config.update_ui_settings({'animation_speed': 0})
    with pytest.raises(ValueError):
        quick_config.update_ui_settings({'animation_speed': -1})
        
    # Invalid color format
    with pytest.raises(ValueError):
        quick_config.update_ui_settings({'background_color': 'invalid'})
    with pytest.raises(ValueError):
        quick_config.update_ui_settings({'font_color': '#XYZ'})
        
    # Invalid language code
    with pytest.raises(ValueError):
        quick_config.update_speech_settings({'language': 'invalid'})
        
    # Invalid timeout values
    with pytest.raises(ValueError):
        quick_config.update_speech_settings({'ambient_duration': -1})
    with pytest.raises(ValueError):
        quick_config.update_speech_settings({'auto_stop_timeout': 0}) 