"""
Configuration module for Mumble Quick
"""

import os
from pathlib import Path
from typing import Dict, Any

from shared.config import ConfigHandler

# Default configuration
DEFAULTS: Dict[str, Any] = {
    # Hotkey settings
    'hotkey': {
        'trigger': 'ctrl+alt',
        'stop': 'esc',
    },
    
    # UI settings
    'ui': {
        'bar_width': 120,
        'bar_height': 20,
        'background_color': '#2C2C2C',
        'foreground_color': '#4CAF50',
        'font_color': '#FFFFFF',
        'opacity': 0.95,
        'animation_speed': 0.3,
        'show_close_button': True,
    },
    
    # Speech recognition settings
    'speech': {
        'language': 'en-US',
        'ambient_duration': 0.5,
        'phrase_timeout': None,
        'auto_stop': True,
        'auto_stop_timeout': 2.0,
    },
    
    # System tray settings
    'tray': {
        'show_notifications': True,
        'minimize_to_tray': True,
        'start_minimized': False,
    },
    
    # Behavior settings
    'behavior': {
        'auto_paste': True,
        'add_trailing_space': True,
        'capitalize_sentences': True,
        'save_position': True,
        'last_position': None,  # Will be updated with actual position
    }
}

class QuickConfig:
    """Configuration manager for Mumble Quick"""
    
    def __init__(self):
        """Initialize configuration"""
        config_dir = Path(__file__).parent
        self.handler = ConfigHandler('quick', config_dir, DEFAULTS)
        
    @property
    def hotkey_trigger(self) -> str:
        """Get hotkey trigger combination"""
        return self.handler.get('hotkey')['trigger']
        
    @hotkey_trigger.setter
    def hotkey_trigger(self, value: str) -> None:
        """Set hotkey trigger combination"""
        current = self.handler.get('hotkey')
        current['trigger'] = value
        self.handler.set('hotkey', current)
        
    @property
    def ui_settings(self) -> Dict[str, Any]:
        """Get UI settings"""
        return self.handler.get('ui')
        
    def update_ui_settings(self, updates: Dict[str, Any]) -> None:
        """Update UI settings"""
        current = self.ui_settings
        current.update(updates)
        self.handler.set('ui', current)
        
    @property
    def speech_settings(self) -> Dict[str, Any]:
        """Get speech recognition settings"""
        return self.handler.get('speech')
        
    def update_speech_settings(self, updates: Dict[str, Any]) -> None:
        """Update speech recognition settings"""
        current = self.speech_settings
        current.update(updates)
        self.handler.set('speech', current)
        
    @property
    def tray_settings(self) -> Dict[str, Any]:
        """Get system tray settings"""
        return self.handler.get('tray')
        
    def update_tray_settings(self, updates: Dict[str, Any]) -> None:
        """Update system tray settings"""
        current = self.tray_settings
        current.update(updates)
        self.handler.set('tray', current)
        
    @property
    def behavior_settings(self) -> Dict[str, Any]:
        """Get behavior settings"""
        return self.handler.get('behavior')
        
    def update_behavior_settings(self, updates: Dict[str, Any]) -> None:
        """Update behavior settings"""
        current = self.behavior_settings
        current.update(updates)
        self.handler.set('behavior', current)
        
    def save_window_position(self, x: int, y: int) -> None:
        """Save window position"""
        current = self.behavior_settings
        current['last_position'] = {'x': x, 'y': y}
        self.handler.set('behavior', current)
        
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults"""
        self.handler.reset() 