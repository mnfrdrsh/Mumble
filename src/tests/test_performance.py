"""
Performance benchmarks for Mumble applications
Measures key performance metrics for both applications
"""

import pytest
import time
import psutil
import os
import tkinter as tk
from unittest.mock import patch
import memory_profiler
from functools import wraps

from mumble_notes.app import MumbleNotes
from mumble_quick.app import MumbleQuick
# from shared.speech_recognition import SpeechRecognizer # Old import
from shared.adaptive_speech import create_adaptive_speech_recognizer # New import
from unittest.mock import MagicMock # Added for mocking recognizer behavior

def measure_time(func):
    """Decorator to measure execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} execution time: {end_time - start_time:.4f} seconds")
        return result
    return wrapper

def measure_memory(func):
    """Decorator to measure memory usage"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
        result = func(*args, **kwargs)
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        print(f"{func.__name__} memory usage: {mem_after - mem_before:.2f} MB")
        return result
    return wrapper

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

class PerformanceBenchmarks:
    """Performance benchmarks for Mumble applications"""
    
    @measure_time
    def test_startup_time(self):
        """Measure application startup time"""
        with patch('tkinter.Tk.mainloop'):
            start_time = time.time()
            notes_app = MumbleNotes()
            notes_startup = time.time() - start_time
            
            start_time = time.time()
            quick_app = MumbleQuick()
            quick_startup = time.time() - start_time
            
            print(f"Mumble Notes startup time: {notes_startup:.4f} seconds")
            print(f"Mumble Quick startup time: {quick_startup:.4f} seconds")
            
            # Cleanup
            notes_app.destroy()
            quick_app.destroy()
            
            # Assert reasonable startup times
            assert notes_startup < 1.0  # Should start in under 1 second
            assert quick_startup < 0.5  # Should start in under 0.5 seconds
    
    @measure_memory
    def test_memory_usage(self, notes_app, quick_app):
        """Measure memory usage during typical operations"""
        # Monitor base memory usage
        process = psutil.Process(os.getpid())
        base_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform typical operations
        for _ in range(10):
            notes_app.editor.insert_text("Test content\n" * 100)
            quick_app.show()
            quick_app.hide()
        
        # Check memory after operations
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - base_memory
        
        print(f"Memory increase: {memory_increase:.2f} MB")
        assert memory_increase < 50  # Should use less than 50MB additional memory
    
    @measure_time
    def test_speech_recognition_performance(self, quick_app):
        """Measure speech recognition related responsiveness in quick_app."""
        # The original test instantiated a local SpeechRecognizer and patched it,
        # which didn't test the app's internal recognizer's performance.
        # This revised test will measure the responsiveness of quick_app.on_speech_recognition()
        # when the internal speech recognizer (AdaptiveSpeechRecognizer) processes a command quickly.

        mock_text_result = "test performance string"

        def mock_start_listening_for_performance(callback_fn, *args, **kwargs):
            # Simulate quick recognition by calling the callback almost immediately
            if callback_fn:
                callback_fn(mock_text_result)
        
        # Replace the app's internal speech_recognizer's start_listening method
        # This assumes quick_app has an attribute 'speech_recognizer' that is an
        # instance of AdaptiveSpeechRecognizer or a compatible object.
        original_recognizer = quick_app.speech_recognizer
        
        # Create a MagicMock for the app's recognizer instance
        mock_app_recognizer = MagicMock()
        mock_app_recognizer.start_listening = MagicMock(side_effect=mock_start_listening_for_performance)
        quick_app.speech_recognizer = mock_app_recognizer

        times = []
        for _ in range(10): # Number of samples
            start_time = time.time()
            # This call should now use the mocked start_listening
            result = quick_app.on_speech_recognition() 
            times.append(time.time() - start_time)
            # We can also assert that the result from on_speech_recognition matches,
            # if on_speech_recognition is designed to return the recognized text.
            assert result == mock_text_result 
        
        avg_time = sum(times) / len(times)
        print(f"Average 'on_speech_recognition' (with mocked recognizer) call time: {avg_time:.4f} seconds")
        # The assertion threshold might need adjustment based on what on_speech_recognition does.
        # This is testing the app's processing overhead more than the recognizer itself.
        assert avg_time < 0.01  # Adjusted threshold: app logic should be very fast with mock.

        # Restore original recognizer if necessary for other tests or cleanup
        quick_app.speech_recognizer = original_recognizer
    
    @measure_time
    def test_document_operations(self, notes_app):
        """Measure document operation performance"""
        # Test large document handling
        large_text = "Test content\n" * 1000
        
        start_time = time.time()
        notes_app.editor.insert_text(large_text)
        insert_time = time.time() - start_time
        
        start_time = time.time()
        notes_app.save_document("large_test.txt")
        save_time = time.time() - start_time
        
        print(f"Large document insert time: {insert_time:.4f} seconds")
        print(f"Large document save time: {save_time:.4f} seconds")
        
        assert insert_time < 0.5  # Should insert in under 0.5 seconds
        assert save_time < 0.3  # Should save in under 0.3 seconds
        
        # Cleanup
        if os.path.exists("large_test.txt"):
            os.remove("large_test.txt")
    
    @measure_time
    def test_ui_responsiveness(self, notes_app, quick_app):
        """Measure UI responsiveness"""
        # Test Mumble Quick show/hide performance
        times = []
        for _ in range(50):
            start_time = time.time()
            quick_app.show()
            quick_app.hide()
            times.append(time.time() - start_time)
        
        avg_time = sum(times) / len(times)
        print(f"Average show/hide time: {avg_time:.4f} seconds")
        assert avg_time < 0.05  # Should take less than 50ms
        
        # Test Mumble Notes UI operations
        start_time = time.time()
        for _ in range(100):
            notes_app.editor.insert_text("test")
            notes_app.editor.delete("1.0", "end")
        ui_time = time.time() - start_time
        
        print(f"UI operation time: {ui_time:.4f} seconds")
        assert ui_time / 100 < 0.01  # Each operation should take less than 10ms

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 