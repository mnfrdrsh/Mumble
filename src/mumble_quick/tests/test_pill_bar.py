"""
Tests for the pill-shaped bar UI component
"""

import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch
import time
import logging

from ..ui.pill_bar import WaveformBar

@pytest.fixture
def bar():
    """Create WaveformBar instance"""
    with patch('tkinter.Tk.mainloop'):  # Prevent mainloop from blocking tests
        bar = WaveformBar()
        yield bar
        bar.destroy()

def test_initialization(bar):
    """Test bar initialization"""
    # Test window properties
    assert bar.winfo_width() == 120
    assert bar.winfo_height() == 20
    assert bar.attributes('-topmost')  # Should stay on top
    assert not bar.wm_overrideredirect()  # No window decorations
    
    # Test canvas setup
    assert isinstance(bar.canvas, tk.Canvas)
    assert bar.canvas.winfo_width() == 120
    assert bar.canvas.winfo_height() == 20
    assert bar.canvas.cget('bg') == '#2C2C2C'
    
    # Test initial state
    assert len(bar.points) == 20
    assert all(p == 0 for p in bar.points)
    assert not bar.is_listening
    assert bar.animation_id is None

def test_pill_shape(bar):
    """Test pill shape creation"""
    # Find pill shape on canvas
    pill = bar.canvas.find_withtag('all')[0]
    
    # Verify it's a polygon
    assert bar.canvas.type(pill) == 'polygon'
    
    # Check pill properties
    coords = bar.canvas.coords(pill)
    assert len(coords) == 16  # 8 points * 2 coordinates
    assert bar.canvas.itemcget(pill, 'fill') == '#2C2C2C'
    assert bar.canvas.itemcget(pill, 'outline') == '#3C3C3C'

def test_close_button(bar):
    """Test close button functionality"""
    # Find close button
    close_btn = None
    for child in bar.winfo_children():
        if isinstance(child, tk.Frame):
            for btn in child.winfo_children():
                if isinstance(btn, tk.Label) and btn.cget('text') == '×':
                    close_btn = btn
                    break
    
    assert close_btn is not None
    assert close_btn.cget('fg') == '#808080'
    assert close_btn.cget('bg') == '#2C2C2C'
    assert close_btn.cget('cursor') == 'hand2'
    
    # Test close functionality
    with patch.object(bar, 'quit') as mock_quit:
        close_btn.event_generate('<Button-1>')
        mock_quit.assert_called_once()

def test_dragging(bar):
    """Test window dragging functionality"""
    initial_x = bar.winfo_x()
    initial_y = bar.winfo_y()
    
    # Simulate drag start
    bar.event_generate('<Button-1>', x=60, y=10)
    
    # Simulate drag motion
    bar.event_generate('<B1-Motion>', x=80, y=15)  # Move 20 right, 5 down
    
    # Verify position change
    assert bar.winfo_x() > initial_x
    assert bar.winfo_y() > initial_y

@patch('random.uniform')
def test_waveform_animation(mock_random, bar):
    """Test waveform animation"""
    # Mock random values for predictable animation
    mock_random.return_value = 1.0
    
    # Start animation
    bar.start_animation()
    assert bar.is_listening
    assert bar.animation_id is not None
    
    # Let animation run for a few frames
    for _ in range(3):
        bar.update()
        time.sleep(0.1)
    
    # Check waveform
    waveform = bar.canvas.find_withtag('waveform')
    assert waveform  # Waveform should exist
    assert bar.canvas.type(waveform[0]) == 'line'
    assert bar.canvas.itemcget(waveform[0], 'fill') == '#4CAF50'
    
    # Stop animation
    bar.stop_animation()
    assert not bar.is_listening
    assert bar.animation_id is None

def test_show_hide(bar):
    """Test show/hide functionality"""
    # Test show
    bar.show()
    assert bar.winfo_viewable()
    assert bar.is_listening
    
    # Verify position (should be at bottom center)
    screen_width = bar.winfo_screenwidth()
    screen_height = bar.winfo_screenheight()
    expected_x = (screen_width - 120) // 2
    expected_y = screen_height - 100
    
    assert abs(bar.winfo_x() - expected_x) <= 1  # Allow 1px difference
    assert abs(bar.winfo_y() - expected_y) <= 1
    
    # Test hide
    bar.hide()
    assert not bar.winfo_viewable()
    assert not bar.is_listening

def test_animation_smoothness(bar):
    """Test animation smoothness and transitions"""
    # Start with zero points
    bar.points = [0] * 20
    
    # Mock random to return increasing values
    values = list(range(20))
    with patch('random.uniform', side_effect=lambda min, max: values.pop(0)):
        bar.start_animation()
        
        # Run a few animation frames
        for _ in range(3):
            bar.update()
            time.sleep(0.05)
        
        # Check that points have been smoothly interpolated
        for point in bar.points:
            assert 0 <= point <= 5  # Points should be within range
            
        # Verify smooth transitions
        differences = [abs(bar.points[i] - bar.points[i-1]) 
                      for i in range(1, len(bar.points))]
        avg_difference = sum(differences) / len(differences)
        assert avg_difference < 2.0  # Transitions should be smooth

def test_error_handling(bar):
    """Test error handling in animations"""
    # Test animation with invalid points
    bar.points = None  # Invalid points
    
    # Should not raise exception
    bar.start_animation()
    bar.update()
    
    # Test with invalid canvas
    bar.canvas.destroy()
    
    # Should handle gracefully
    bar.start_animation()
    bar.stop_animation()

def test_memory_management(bar):
    """Test memory management during animations"""
    initial_widgets = len(bar.winfo_children())
    
    # Run multiple animation cycles
    for _ in range(5):
        bar.start_animation()
        bar.update()
        bar.stop_animation()
    
    # Verify no widget leaks
    final_widgets = len(bar.winfo_children())
    assert final_widgets == initial_widgets
    
    # Verify canvas items are cleaned up
    waveform_items = len(bar.canvas.find_withtag('waveform'))
    assert waveform_items <= 1  # Should only be 0 or 1 waveform

def test_performance(bar):
    """Test animation performance"""
    frame_times = []
    
    # Measure frame render times
    bar.start_animation()
    for _ in range(10):
        start = time.perf_counter()
        bar.update()
        frame_times.append(time.perf_counter() - start)
    bar.stop_animation()
    
    # Average frame time should be reasonable
    avg_frame_time = sum(frame_times) / len(frame_times)
    assert avg_frame_time < 0.1  # Should take less than 100ms per frame 