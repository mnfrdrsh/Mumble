"""
Tests for shared configuration handler
"""

import os
import json
import pytest
from pathlib import Path
from typing import Dict, Any

from ..config import ConfigHandler

@pytest.fixture
def temp_config_dir(tmp_path) -> Path:
    """Create temporary config directory"""
    return tmp_path / "config"

@pytest.fixture
def default_config() -> Dict[str, Any]:
    """Default test configuration"""
    return {
        'test_str': 'default',
        'test_int': 42,
        'test_float': 3.14,
        'test_bool': True,
        'test_list': ['a', 'b', 'c'],
        'test_dict': {
            'key1': 'value1',
            'key2': 'value2'
        }
    }

@pytest.fixture
def config_handler(temp_config_dir, default_config) -> ConfigHandler:
    """Create ConfigHandler instance"""
    return ConfigHandler('test', temp_config_dir, default_config)

def test_init_creates_config_dir(temp_config_dir, default_config):
    """Test that initialization creates config directory"""
    ConfigHandler('test', temp_config_dir, default_config)
    assert temp_config_dir.exists()
    assert temp_config_dir.is_dir()

def test_init_creates_config_file(temp_config_dir, default_config):
    """Test that initialization creates config file with defaults"""
    handler = ConfigHandler('test', temp_config_dir, default_config)
    config_file = temp_config_dir / "test_config.json"
    
    assert config_file.exists()
    assert config_file.is_file()
    
    with open(config_file, 'r') as f:
        saved_config = json.load(f)
    assert saved_config == default_config

def test_get_existing_key(config_handler, default_config):
    """Test getting existing configuration value"""
    assert config_handler.get('test_str') == default_config['test_str']
    assert config_handler.get('test_int') == default_config['test_int']
    assert config_handler.get('test_float') == default_config['test_float']
    assert config_handler.get('test_bool') == default_config['test_bool']
    assert config_handler.get('test_list') == default_config['test_list']
    assert config_handler.get('test_dict') == default_config['test_dict']

def test_get_nonexistent_key(config_handler):
    """Test getting nonexistent configuration value"""
    assert config_handler.get('nonexistent') is None
    assert config_handler.get('nonexistent', 'default') == 'default'

def test_set_new_value(config_handler):
    """Test setting new configuration value"""
    config_handler.set('new_key', 'new_value')
    assert config_handler.get('new_key') == 'new_value'
    
    # Verify persistence
    config_handler.load_config()
    assert config_handler.get('new_key') == 'new_value'

def test_set_existing_value(config_handler):
    """Test updating existing configuration value"""
    config_handler.set('test_str', 'updated')
    assert config_handler.get('test_str') == 'updated'
    
    # Verify persistence
    config_handler.load_config()
    assert config_handler.get('test_str') == 'updated'

def test_update_multiple_values(config_handler):
    """Test updating multiple configuration values"""
    updates = {
        'test_str': 'updated',
        'test_int': 100,
        'new_key': 'new_value'
    }
    config_handler.update(updates)
    
    assert config_handler.get('test_str') == 'updated'
    assert config_handler.get('test_int') == 100
    assert config_handler.get('new_key') == 'new_value'
    
    # Verify persistence
    config_handler.load_config()
    assert config_handler.get('test_str') == 'updated'
    assert config_handler.get('test_int') == 100
    assert config_handler.get('new_key') == 'new_value'

def test_reset_to_defaults(config_handler, default_config):
    """Test resetting configuration to defaults"""
    # Modify some values
    config_handler.set('test_str', 'modified')
    config_handler.set('new_key', 'new_value')
    
    # Reset to defaults
    config_handler.reset()
    
    # Verify all values are back to defaults
    for key, value in default_config.items():
        assert config_handler.get(key) == value
    
    # Verify new key is removed
    assert config_handler.get('new_key') is None
    
    # Verify persistence
    config_handler.load_config()
    for key, value in default_config.items():
        assert config_handler.get(key) == value
    assert config_handler.get('new_key') is None

def test_load_invalid_config(config_handler):
    """Test loading invalid configuration file"""
    # Write invalid JSON
    config_file = Path(config_handler.config_dir) / "test_config.json"
    with open(config_file, 'w') as f:
        f.write('invalid json')
    
    # Load should fall back to defaults
    config_handler.load_config()
    assert config_handler.get('test_str') == 'default'

def test_save_error_handling(config_handler, monkeypatch):
    """Test error handling when saving configuration"""
    def mock_dump(*args, **kwargs):
        raise IOError("Mock save error")
    
    monkeypatch.setattr(json, 'dump', mock_dump)
    
    # Should not raise exception
    config_handler.save_config()
    
    # Config should still be accessible
    assert config_handler.get('test_str') == 'default'

def test_config_type_preservation(config_handler):
    """Test that value types are preserved"""
    values = {
        'string': 'test',
        'integer': 42,
        'float': 3.14,
        'boolean': True,
        'list': [1, 2, 3],
        'dict': {'key': 'value'}
    }
    
    # Set values
    for key, value in values.items():
        config_handler.set(key, value)
    
    # Verify types after load
    config_handler.load_config()
    for key, value in values.items():
        assert isinstance(config_handler.get(key), type(value))
        assert config_handler.get(key) == value 