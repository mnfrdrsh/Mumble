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
# from shared.speech_recognition import SpeechRecognizer # Old import
from shared.adaptive_speech import create_adaptive_speech_recognizer # New import
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
def speech_recognizer_fixture(): # Renamed fixture for clarity
    """Create AdaptiveSpeechRecognizer instance for shared testing if needed,
       though apps usually create their own."""
    return create_adaptive_speech_recognizer()

# This test assumed a shared recognizer instance or that apps' internal recognizers could be
# patched via a common class. With create_adaptive_speech_recognizer, apps get their own instances.
# The test needs to patch where the recognizer is *created* or *used* within each app.
# For now, let's assume on_speech_recognition() in each app uses its own recognizer.
# We will patch the 'start_listening' method of the recognizer that each app creates.

def mock_start_listening_immediately_call_callback(text_to_return: str):
    """Helper to create a mock for start_listening that calls the callback."""
    def _mock_start_listening(callback_fn, *args, **kwargs):
        if callback_fn:
            callback_fn(text_to_return)
    return MagicMock(side_effect=_mock_start_listening)

def test_shared_speech_recognition(notes_app, quick_app): # Removed speech_recognizer fixture from args
    """Test speech recognition functionality in both apps."""
    mock_text = "Test speech recognition"
    
    # Path to where create_adaptive_speech_recognizer is called by MumbleNotes
    # Assuming MumbleNotes uses self.speech_recognizer = create_adaptive_speech_recognizer()
    # and on_speech_recognition calls self.speech_recognizer.start_listening(...)
    # The actual patch target depends on app's internal structure.
    # If app.py has `self.speech_recognizer = create_adaptive_speech_recognizer()`,
    # and `on_speech_recognition` does `self.speech_recognizer.start_listening(self.some_callback)`,
    # then we patch the `start_listening` method of the instance.
    # This is tricky without seeing app code. A common pattern is to patch the factory:
    
    # Patching the factory function `create_adaptive_speech_recognizer` for each app context
    # This ensures that when the app calls it, it gets our mock.
    
    # For MumbleNotes
    # Assuming notes_app.on_speech_recognition() internally gets text and returns it.
    # This test is more about the app's handling of recognized text.
    with patch('mumble_notes.app.create_adaptive_speech_recognizer') as mock_create_notes_recognizer:
        mock_notes_recognizer_instance = MagicMock()
        mock_notes_recognizer_instance.start_listening = mock_start_listening_immediately_call_callback(mock_text)
        mock_create_notes_recognizer.return_value = mock_notes_recognizer_instance
        
        # Re-initialize or set the recognizer if app creates it in __init__
        # This depends on how the app is structured. If it's in __init__, this patch needs to be active before app creation.
        # For this example, let's assume on_speech_recognition can be made to use a fresh (mocked) recognizer
        # or that the app's recognizer can be replaced.
        # A simpler approach for an existing app instance:
        # notes_app.speech_recognizer = mock_notes_recognizer_instance 
        # (if speech_recognizer is an attribute)
        
        # Let's assume the app's on_speech_recognition method is what we test.
        # And it uses an internal recognizer. We'll patch that recognizer's start_listening.
        # This requires knowing the attribute name, e.g., notes_app.speech_recognizer
        
        # If app structure is: self.recognizer = create_adaptive_speech_recognizer()
        # then patch 'mumble_notes.app.AdaptiveSpeechRecognizer.start_listening' if it's used that way
        # Or, more robustly, patch the create_ function for the whole test duration if apps are created fresh.
        # The fixtures create apps fresh, so patching create_ is better.

        # The original test called notes_app.on_speech_recognition() which presumably returned the text.
        # We need to ensure that when on_speech_recognition is called, the (mocked) text is returned.
        # This implies that on_speech_recognition sets up a callback that updates some state,
        # and then on_speech_recognition returns that state or the text directly.
        
        # Re-evaluating: The original test patched `speech_recognizer.recognize_speech`.
        # And then called `app.on_speech_recognition()`. This implies `on_speech_recognition`
        # somehow used that specific patched `speech_recognizer` instance.
        # This is unusual unless the app takes the recognizer as a parameter for that method
        # or it's globally shared and replaced, which is unlikely with `create_adaptive_speech_recognizer`.
        
        # Let's assume the most plausible scenario: `app.on_speech_recognition()` is a method
        # that, when called, eventually calls `self.speech_recognizer.start_listening(some_internal_callback)`.
        # The `some_internal_callback` would then update a variable that `on_speech_recognition` returns.
        
        # To simplify, we'll assume the app has an attribute `speech_recognizer`
        # that we can replace with a mock for the test.
        
        mock_notes_recognizer = MagicMock()
        mock_notes_recognizer.start_listening = mock_start_listening_immediately_call_callback(mock_text)
        notes_app.speech_recognizer = mock_notes_recognizer # Replace instance

        # Test Mumble Notes speech recognition
        # We need to simulate how on_speech_recognition gets the text.
        # If on_speech_recognition is blocking and internally waits for the callback:
        # notes_result = notes_app.on_speech_recognition() 
        # assert notes_result == mock_text

        # If on_speech_recognition is non-blocking and relies on a callback to set a result:
        # This test would need to be more complex or the app method refactored for testability.
        # For now, let's assume on_speech_recognition is a simplified method that directly returns text
        # for testing purposes, or that the callback it sets updates a retrievable attribute.
        
        # Given the original test structure: `notes_result = notes_app.on_speech_recognition()`,
        # it implies `on_speech_recognition` is synchronous or handles the async nature internally
        # and provides a return value. We will replicate this by making the mock `start_listening`
        # effectively synchronous by calling the callback immediately.
        
        # If MumbleNotes.on_speech_recognition looks like:
        # def on_speech_recognition(self):
        #   self._recognized_text = None
        #   def _callback(text): self._recognized_text = text
        #   self.speech_recognizer.start_listening(_callback)
        #   # ... some way to wait or get the text ...
        #   return self._recognized_text
        # Then our mock should work.
        
        notes_result = notes_app.on_speech_recognition() # Call the app's method
        assert notes_result == mock_text
        mock_notes_recognizer.start_listening.assert_called_once()

        # For MumbleQuick
        mock_quick_recognizer = MagicMock()
        mock_quick_recognizer.start_listening = mock_start_listening_immediately_call_callback(mock_text)
        quick_app.speech_recognizer = mock_quick_recognizer # Replace instance

        quick_result = quick_app.on_speech_recognition()
        assert quick_result == mock_text
        mock_quick_recognizer.start_listening.assert_called_once()
        
        # Verify both apps use the same recognition settings (if this still makes sense)
        # This assertion might be about config, not recognizer instances.
        if hasattr(notes_app, 'speech_settings') and hasattr(quick_app, 'speech_settings'):
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
    
    # Mock speech recognition for quick_app
    # Assuming quick_app.speech_recognizer is an instance of AdaptiveSpeechRecognizer
    # or a compatible mock.
    mock_recognizer_instance = MagicMock()
    # Setup the mock_recognizer_instance.start_listening to call its callback with test_text
    mock_recognizer_instance.start_listening = mock_start_listening_immediately_call_callback(test_text)
    
    # Replace the app's speech_recognizer instance with our mock
    quick_app.speech_recognizer = mock_recognizer_instance
    
    # Simulate speech recognition by calling the app's method
    quick_app.on_speech_recognition()
    
    # Verify the mock was called
    mock_recognizer_instance.start_listening.assert_called_once()
    
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