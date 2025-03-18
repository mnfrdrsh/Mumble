"""
Configuration module for Mumble Notes
"""

import os
from pathlib import Path
from typing import Dict, Any, List

from shared.config import ConfigHandler

# Default configuration
DEFAULTS: Dict[str, Any] = {
    # Window settings
    'window': {
        'width': 1200,
        'height': 800,
        'position': None,  # Will be updated with actual position
        'maximized': False,
    },
    
    # Editor settings
    'editor': {
        'font_family': 'Arial',
        'font_size': 12,
        'line_spacing': 1.2,
        'tab_size': 4,
        'wrap_text': True,
        'show_line_numbers': False,
        'auto_save': True,
        'auto_save_interval': 300,  # 5 minutes
    },
    
    # Theme settings
    'theme': {
        'name': 'clam',
        'background_color': '#FFFFFF',
        'text_color': '#000000',
        'accent_color': '#4CAF50',
        'sidebar_width': 250,
    },
    
    # Document settings
    'documents': {
        'storage_path': 'documents',  # Relative to config directory
        'default_format': 'rtf',
        'backup_enabled': True,
        'backup_count': 5,
        'categories': ['Notes', 'Documents', 'Templates'],
    },
    
    # Speech recognition settings
    'speech': {
        'language': 'en-US',
        'ambient_duration': 0.5,
        'auto_punctuate': True,
        'capitalize_sentences': True,
    }
}

class NotesConfig:
    """Configuration manager for Mumble Notes"""
    
    def __init__(self):
        """Initialize configuration"""
        config_dir = Path(__file__).parent
        self.handler = ConfigHandler('notes', config_dir, DEFAULTS)
        
        # Ensure document storage directory exists
        self.documents_path.mkdir(parents=True, exist_ok=True)
        
    @property
    def documents_path(self) -> Path:
        """Get path to documents storage"""
        storage_path = self.handler.get('documents')['storage_path']
        return Path(self.handler.config_dir) / storage_path
        
    @property
    def window_settings(self) -> Dict[str, Any]:
        """Get window settings"""
        return self.handler.get('window')
        
    def update_window_settings(self, updates: Dict[str, Any]) -> None:
        """Update window settings"""
        current = self.window_settings
        current.update(updates)
        self.handler.set('window', current)
        
    @property
    def editor_settings(self) -> Dict[str, Any]:
        """Get editor settings"""
        return self.handler.get('editor')
        
    def update_editor_settings(self, updates: Dict[str, Any]) -> None:
        """Update editor settings"""
        current = self.editor_settings
        current.update(updates)
        self.handler.set('editor', current)
        
    @property
    def theme_settings(self) -> Dict[str, Any]:
        """Get theme settings"""
        return self.handler.get('theme')
        
    def update_theme_settings(self, updates: Dict[str, Any]) -> None:
        """Update theme settings"""
        current = self.theme_settings
        current.update(updates)
        self.handler.set('theme', current)
        
    @property
    def document_settings(self) -> Dict[str, Any]:
        """Get document settings"""
        return self.handler.get('documents')
        
    def update_document_settings(self, updates: Dict[str, Any]) -> None:
        """Update document settings"""
        current = self.document_settings
        current.update(updates)
        self.handler.set('documents', current)
        
    def add_category(self, category: str) -> None:
        """Add a new document category"""
        current = self.document_settings
        if category not in current['categories']:
            current['categories'].append(category)
            self.handler.set('documents', current)
            
    def remove_category(self, category: str) -> None:
        """Remove a document category"""
        current = self.document_settings
        if category in current['categories']:
            current['categories'].remove(category)
            self.handler.set('documents', current)
            
    @property
    def speech_settings(self) -> Dict[str, Any]:
        """Get speech recognition settings"""
        return self.handler.get('speech')
        
    def update_speech_settings(self, updates: Dict[str, Any]) -> None:
        """Update speech recognition settings"""
        current = self.speech_settings
        current.update(updates)
        self.handler.set('speech', current)
        
    def save_window_position(self, x: int, y: int, width: int, height: int, maximized: bool) -> None:
        """Save window position and size"""
        self.update_window_settings({
            'position': {'x': x, 'y': y},
            'width': width,
            'height': height,
            'maximized': maximized
        })
        
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults"""
        self.handler.reset() 