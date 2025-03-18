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
from shared.speech_recognition import SpeechRecognizer

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
        """Measure speech recognition performance"""
        recognizer = SpeechRecognizer()
        
        # Measure recognition time for 10 samples
        times = []
        for _ in range(10):
            start_time = time.time()
            with patch.object(recognizer, 'recognize_speech', return_value="test"):
                quick_app.on_speech_recognition()
            times.append(time.time() - start_time)
        
        avg_time = sum(times) / len(times)
        print(f"Average speech recognition time: {avg_time:.4f} seconds")
        assert avg_time < 0.1  # Should process in under 0.1 seconds
    
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