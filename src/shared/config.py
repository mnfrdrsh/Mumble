"""
Shared configuration handler for Mumble applications
"""

import os
import json
import logging
from typing import Any, Dict, Optional
from pathlib import Path

class ConfigHandler:
    """Configuration handler with validation and persistence"""
    
    def __init__(self, app_name: str, config_dir: str, defaults: Dict[str, Any]):
        """
        Initialize configuration handler
        
        Args:
            app_name: Name of the application (e.g., 'notes' or 'quick')
            config_dir: Directory to store configuration files
            defaults: Default configuration values
        """
        self.logger = logging.getLogger(f'mumble.{app_name}.config')
        self.app_name = app_name
        self.config_dir = Path(config_dir)
        self.defaults = defaults
        self.config_file = self.config_dir / f"{app_name}_config.json"
        self.config: Dict[str, Any] = {}
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or create configuration
        self.load_config()
        
    def load_config(self) -> None:
        """Load configuration from file or create with defaults"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                self.logger.info(f"Loaded configuration from {self.config_file}")
            else:
                self.config = self.defaults.copy()
                self.save_config()
                self.logger.info("Created new configuration with defaults")
                
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            self.config = self.defaults.copy()
            
    def save_config(self) -> None:
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            self.logger.info(f"Saved configuration to {self.config_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            key: Configuration key
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default or self.defaults.get(key))
        
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value and save
        
        Args:
            key: Configuration key
            value: Value to set
        """
        self.config[key] = value
        self.save_config()
        
    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update multiple configuration values and save
        
        Args:
            updates: Dictionary of updates
        """
        self.config.update(updates)
        self.save_config()
        
    def reset(self) -> None:
        """Reset configuration to defaults"""
        self.config = self.defaults.copy()
        self.save_config()
        self.logger.info("Reset configuration to defaults") 