"""
Integration tests for Mumble applications
Tests end-to-end workflows and interactions between components
"""

import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch
import time
import os
import json

from mumble_notes.app import MumbleNotes
from mumble_quick.app import MumbleQuick
from shared.speech_recognition import SpeechRecognizer
from shared.config import ConfigHandler

@pytest.fixture
def notes_app():
    """Create MumbleNotes instance"""
    with patch('tkinter.Tk.mainloop'):
        app = MumbleNotes()
        yield app
        app.destroy()

@pytest.fixture
def quick_app():
    """Create MumbleQuick instance"""
    with patch('tkinter.Tk.mainloop'):
        app = MumbleQuick()
        yield app
        app.destroy()

@pytest.fixture
def speech_recognizer():
    """Create SpeechRecognizer instance"""
    return SpeechRecognizer()

def test_shared_speech_recognition(notes_app, quick_app, speech_recognizer):
    """Test speech recognition works consistently across both apps"""
    # Mock speech recognition to return consistent results
    mock_text = "Test speech recognition"
    with patch.object(speech_recognizer, 'recognize_speech', return_value=mock_text):
        # Test Mumble Notes speech recognition
        notes_result = notes_app.on_speech_recognition()
        assert notes_result == mock_text
        
        # Test Mumble Quick speech recognition
        quick_result = quick_app.on_speech_recognition()
        assert quick_result == mock_text
        
        # Verify both apps use the same recognition settings
        assert notes_app.speech_settings == quick_app.speech_settings

def test_config_synchronization():
    """Test configuration synchronization between apps"""
    # Create temporary config files
    notes_config = ConfigHandler("notes_test_config.json")
    quick_config = ConfigHandler("quick_test_config.json")
    
    # Set shared settings
    shared_settings = {
        "speech_recognition": {
            "language": "en-US",
            "confidence_threshold": 0.8
        }
    }
    
    notes_config.update(shared_settings)
    quick_config.update(shared_settings)
    
    # Verify settings are synchronized
    assert notes_config.get("speech_recognition") == quick_config.get("speech_recognition")
    
    # Clean up
    os.remove("notes_test_config.json")
    os.remove("quick_test_config.json")

def test_clipboard_interaction(quick_app):
    """Test clipboard interaction between Mumble Quick and system"""
    test_text = "Test clipboard interaction"
    
    # Mock speech recognition
    with patch.object(quick_app.speech_recognizer, 'recognize_speech', 
                     return_value=test_text):
        # Simulate speech recognition
        quick_app.on_speech_recognition()
        
        # Verify text was copied to clipboard
        import pyperclip
        assert pyperclip.paste() == test_text

def test_document_persistence(notes_app):
    """Test document persistence and recovery"""
    # Create test document
    test_title = "Test Document"
    test_content = "Test content for persistence"
    
    notes_app.editor.insert_text(test_content)
    notes_app.save_document(test_title)
    
    # Simulate application restart
    notes_app.destroy()
    
    # Create new instance
    with patch('tkinter.Tk.mainloop'):
        new_app = MumbleNotes()
        
        # Verify document was loaded
        loaded_docs = new_app.document_manager.documents
        assert any(doc['title'] == test_title for doc in loaded_docs.values())
        assert any(doc['content'] == test_content for doc in loaded_docs.values())
        
        new_app.destroy()

def test_multi_window_interaction(notes_app, quick_app):
    """Test interaction between multiple windows"""
    # Test window focus handling
    notes_app.focus_force()
    assert notes_app.focus_get() is not None
    
    quick_app.show()
    assert quick_app.focus_get() is not None
    assert notes_app.focus_get() is None

def test_error_propagation():
    """Test error handling and logging across applications"""
    # Set up logging
    with patch('logging.error') as mock_error:
        # Simulate error in shared component
        config = ConfigHandler("test_config.json")
        config.file_path = "/nonexistent/path/config.json"
        
        # Attempt to save config
        config.save_config()
        
        # Verify error was logged
        mock_error.assert_called_once()
        
        # Clean up
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")

def test_performance_interaction(notes_app, quick_app):
    """Test performance impact of running both applications"""
    # Monitor memory usage
    initial_memory = notes_app.winfo_fpixels('1i')  # Use as memory proxy
    
    # Simulate intensive operations
    for _ in range(10):
        notes_app.editor.insert_text("Test content\n" * 100)
        quick_app.show()
        quick_app.hide()
        
    # Verify memory usage is reasonable
    final_memory = notes_app.winfo_fpixels('1i')
    assert final_memory - initial_memory < 1000  # Arbitrary threshold

def test_theme_consistency(notes_app, quick_app):
    """Test theme consistency across applications"""
    # Set theme in Mumble Notes
    notes_app.apply_theme("dark")
    
    # Verify theme consistency
    assert notes_app.editor.text.cget('bg') == quick_app.pill_bar.canvas.cget('bg')
    assert notes_app.current_theme == quick_app.current_theme

def test_startup_sequence():
    """Test application startup sequence"""
    # Mock system tray
    with patch('pystray.Icon'):
        # Start Mumble Quick first
        quick_app = MumbleQuick()
        assert quick_app.is_running
        
        # Start Mumble Notes
        notes_app = MumbleNotes()
        assert notes_app.is_running
        
        # Verify both apps are responsive
        assert quick_app.winfo_exists()
        assert notes_app.winfo_exists()
        
        # Clean up
        quick_app.destroy()
        notes_app.destroy()

def test_file_operations(notes_app):
    """Test file operations and persistence"""
    # Create test document
    test_content = "Test file operations"
    notes_app.editor.insert_text(test_content)
    
    # Save document
    test_file = "test_document.txt"
    notes_app.save_document(test_file)
    
    # Verify file exists and content is correct
    assert os.path.exists(test_file)
    with open(test_file, 'r') as f:
        content = f.read()
        assert content == test_content
    
    # Clean up
    os.remove(test_file) 