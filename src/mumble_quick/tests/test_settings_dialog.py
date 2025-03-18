"""
Tests for Mumble Quick settings dialog
"""

import pytest
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from unittest.mock import MagicMock, patch

from ..config.quick_config import QuickConfig
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
def quick_config(temp_config_dir) -> QuickConfig:
    """Create QuickConfig instance with temporary directory"""
    config = QuickConfig()
    config.handler.config_dir = temp_config_dir
    config.handler.config_file = temp_config_dir / "quick_config.json"
    config.handler.save_config()
    return config

@pytest.fixture
def dialog(root, quick_config):
    """Create settings dialog"""
    dialog = SettingsDialog(root, quick_config)
    return dialog

def test_dialog_initialization(dialog):
    """Test dialog initialization"""
    assert dialog.title() == "Mumble Quick Settings"
    assert isinstance(dialog.notebook, ttk.Notebook)
    assert len(dialog.notebook.tabs()) == 5  # Hotkeys, UI, Speech, System Tray, Behavior

def test_hotkey_tab_widgets(dialog):
    """Test hotkey tab widgets"""
    assert isinstance(dialog.hotkey_trigger, ttk.Entry)
    assert isinstance(dialog.hotkey_stop, ttk.Entry)

def test_ui_tab_widgets(dialog):
    """Test UI tab widgets"""
    assert isinstance(dialog.bar_width, ttk.Spinbox)
    assert isinstance(dialog.bar_height, ttk.Spinbox)
    assert isinstance(dialog.bg_color, tk.StringVar)
    assert isinstance(dialog.fg_color, tk.StringVar)
    assert isinstance(dialog.font_color, tk.StringVar)
    assert isinstance(dialog.opacity, ttk.Scale)
    assert isinstance(dialog.animation_speed, ttk.Scale)
    assert isinstance(dialog.show_close_button, tk.BooleanVar)

def test_speech_tab_widgets(dialog):
    """Test speech tab widgets"""
    assert isinstance(dialog.language, ttk.Combobox)
    assert isinstance(dialog.ambient_duration, ttk.Spinbox)
    assert isinstance(dialog.phrase_timeout, ttk.Spinbox)
    assert isinstance(dialog.auto_stop, tk.BooleanVar)
    assert isinstance(dialog.auto_stop_timeout, ttk.Spinbox)

def test_tray_tab_widgets(dialog):
    """Test system tray tab widgets"""
    assert isinstance(dialog.show_notifications, tk.BooleanVar)
    assert isinstance(dialog.minimize_to_tray, tk.BooleanVar)
    assert isinstance(dialog.start_minimized, tk.BooleanVar)

def test_behavior_tab_widgets(dialog):
    """Test behavior tab widgets"""
    assert isinstance(dialog.auto_paste, tk.BooleanVar)
    assert isinstance(dialog.add_trailing_space, tk.BooleanVar)
    assert isinstance(dialog.capitalize_sentences, tk.BooleanVar)
    assert isinstance(dialog.save_position, tk.BooleanVar)

def test_load_settings(dialog, quick_config):
    """Test loading settings into UI"""
    # Hotkey settings
    hotkey = quick_config.handler.get('hotkey')
    assert dialog.hotkey_trigger.get() == hotkey['trigger']
    assert dialog.hotkey_stop.get() == hotkey['stop']
    
    # UI settings
    ui = quick_config.ui_settings
    assert int(dialog.bar_width.get()) == ui['bar_width']
    assert int(dialog.bar_height.get()) == ui['bar_height']
    assert dialog.bg_color.get() == ui['background_color']
    assert dialog.fg_color.get() == ui['foreground_color']
    assert dialog.font_color.get() == ui['font_color']
    assert float(dialog.opacity.get()) == ui['opacity']
    assert float(dialog.animation_speed.get()) == ui['animation_speed']
    assert dialog.show_close_button.get() == ui['show_close_button']
    
    # Speech settings
    speech = quick_config.speech_settings
    assert dialog.language.get() == speech['language']
    assert float(dialog.ambient_duration.get()) == speech['ambient_duration']
    assert dialog.phrase_timeout.get() == str(speech['phrase_timeout'] or '')
    assert dialog.auto_stop.get() == speech['auto_stop']
    assert float(dialog.auto_stop_timeout.get()) == speech['auto_stop_timeout']
    
    # Tray settings
    tray = quick_config.tray_settings
    assert dialog.show_notifications.get() == tray['show_notifications']
    assert dialog.minimize_to_tray.get() == tray['minimize_to_tray']
    assert dialog.start_minimized.get() == tray['start_minimized']
    
    # Behavior settings
    behavior = quick_config.behavior_settings
    assert dialog.auto_paste.get() == behavior['auto_paste']
    assert dialog.add_trailing_space.get() == behavior['add_trailing_space']
    assert dialog.capitalize_sentences.get() == behavior['capitalize_sentences']
    assert dialog.save_position.get() == behavior['save_position']

def test_apply_settings(dialog, quick_config):
    """Test applying settings from UI"""
    # Modify UI values
    dialog.hotkey_trigger.delete(0, tk.END)
    dialog.hotkey_trigger.insert(0, 'ctrl+shift')
    dialog.hotkey_stop.delete(0, tk.END)
    dialog.hotkey_stop.insert(0, 'alt')
    
    dialog.bar_width.set('150')
    dialog.bar_height.set('30')
    dialog.bg_color.set('#333333')
    dialog.fg_color.set('#00FF00')
    dialog.font_color.set('#CCCCCC')
    dialog.opacity.set(0.8)
    dialog.animation_speed.set(0.5)
    dialog.show_close_button.set(False)
    
    dialog.language.set('en-GB')
    dialog.ambient_duration.set('1.0')
    dialog.phrase_timeout.set('5.0')
    dialog.auto_stop.set(False)
    dialog.auto_stop_timeout.set('3.0')
    
    dialog.show_notifications.set(False)
    dialog.minimize_to_tray.set(False)
    dialog.start_minimized.set(True)
    
    dialog.auto_paste.set(False)
    dialog.add_trailing_space.set(False)
    dialog.capitalize_sentences.set(False)
    dialog.save_position.set(False)
    
    # Apply settings
    dialog._apply_settings()
    
    # Verify config values
    hotkey = quick_config.handler.get('hotkey')
    assert hotkey['trigger'] == 'ctrl+shift'
    assert hotkey['stop'] == 'alt'
    
    ui = quick_config.ui_settings
    assert ui['bar_width'] == 150
    assert ui['bar_height'] == 30
    assert ui['background_color'] == '#333333'
    assert ui['foreground_color'] == '#00FF00'
    assert ui['font_color'] == '#CCCCCC'
    assert ui['opacity'] == 0.8
    assert ui['animation_speed'] == 0.5
    assert ui['show_close_button'] is False
    
    speech = quick_config.speech_settings
    assert speech['language'] == 'en-GB'
    assert speech['ambient_duration'] == 1.0
    assert speech['phrase_timeout'] == 5.0
    assert speech['auto_stop'] is False
    assert speech['auto_stop_timeout'] == 3.0
    
    tray = quick_config.tray_settings
    assert tray['show_notifications'] is False
    assert tray['minimize_to_tray'] is False
    assert tray['start_minimized'] is True
    
    behavior = quick_config.behavior_settings
    assert behavior['auto_paste'] is False
    assert behavior['add_trailing_space'] is False
    assert behavior['capitalize_sentences'] is False
    assert behavior['save_position'] is False

def test_reset_defaults(dialog, quick_config):
    """Test resetting settings to defaults"""
    # Modify settings
    dialog.hotkey_trigger.delete(0, tk.END)
    dialog.hotkey_trigger.insert(0, 'ctrl+shift')
    dialog.bar_width.set('150')
    dialog.language.set('en-GB')
    dialog.show_notifications.set(False)
    dialog.auto_paste.set(False)
    
    # Mock messagebox.askyesno to return True
    with patch('tkinter.messagebox.askyesno', return_value=True):
        dialog._reset_defaults()
    
    # Verify UI values are reset
    hotkey = quick_config.handler.get('hotkey')
    assert dialog.hotkey_trigger.get() == hotkey['trigger']
    assert int(dialog.bar_width.get()) == quick_config.ui_settings['bar_width']
    assert dialog.language.get() == quick_config.speech_settings['language']
    assert dialog.show_notifications.get() == quick_config.tray_settings['show_notifications']
    assert dialog.auto_paste.get() == quick_config.behavior_settings['auto_paste']

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