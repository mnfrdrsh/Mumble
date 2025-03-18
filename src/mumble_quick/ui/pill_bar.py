"""
Animated pill-shaped bar UI for Mumble Quick
"""

import tkinter as tk
import math
import random
from typing import List, Optional
import logging
import traceback

class WaveformBar(tk.Tk):
    """A pill-shaped bar with animated waveform visualization"""
    
    def __init__(self):
        try:
            super().__init__()
            self.logger = logging.getLogger('mumble.quick.ui')
            self.logger.info("Initializing WaveformBar")
            
            # Configure window
            self.overrideredirect(True)  # Remove window decorations
            self.attributes('-topmost', True)  # Keep window on top
            self.configure(bg='#2C2C2C')
            
            # Set window size (120x20 pixels)
            self.geometry('120x20')
            
            # Create canvas for waveform
            self.canvas = tk.Canvas(
                self,
                width=120,
                height=20,
                bg='#2C2C2C',
                highlightthickness=0
            )
            self.canvas.pack(fill=tk.BOTH, expand=True)
            
            # Initialize waveform variables
            self.points: List[float] = [0] * 20  # Points for the waveform
            self.is_listening = False
            self.animation_id: Optional[str] = None
            
            # Round the window corners for pill shape
            self._create_pill_shape()
            
            # Add close button
            self._add_close_button()
            
            # Enable window dragging
            self._enable_drag()
            
            self.logger.info("WaveformBar initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing WaveformBar: {e}")
            self.logger.error(traceback.format_exc())
            raise
            
    def _create_pill_shape(self):
        """Create the pill shape using a rounded rectangle"""
        try:
            def _create_rounded_rect():
                radius = 10
                points = [
                    radius, 0,  # Top left
                    120 - radius, 0,  # Top right
                    120, radius,  # Right top
                    120, 20 - radius,  # Right bottom
                    120 - radius, 20,  # Bottom right
                    radius, 20,  # Bottom left
                    0, 20 - radius,  # Left bottom
                    0, radius  # Left top
                ]
                return points
                
            # Create mask
            self.mask = self.canvas.create_polygon(
                _create_rounded_rect(),
                smooth=True,
                fill='#2C2C2C',
                outline='#3C3C3C'
            )
            self.logger.info("Pill shape created")
        except Exception as e:
            self.logger.error(f"Error creating pill shape: {e}")
            self.logger.error(traceback.format_exc())
            
    def _add_close_button(self):
        """Add a subtle close button"""
        size = 12
        padding = 4
        
        # Create close button frame
        close_frame = tk.Frame(
            self,
            width=size,
            height=size,
            bg='#2C2C2C'
        )
        close_frame.place(x=120-size-padding, y=padding)
        
        # Create close button
        close_btn = tk.Label(
            close_frame,
            text='×',
            fg='#808080',
            bg='#2C2C2C',
            font=('Arial', 8),
            cursor='hand2'
        )
        close_btn.pack()
        close_btn.bind('<Button-1>', lambda e: self.quit())
        
    def _enable_drag(self):
        """Enable window dragging"""
        self.bind('<Button-1>', self._on_drag_start)
        self.bind('<B1-Motion>', self._on_drag_motion)
        
    def _on_drag_start(self, event):
        """Store initial position for dragging"""
        self._drag_data = {'x': event.x, 'y': event.y}
        
    def _on_drag_motion(self, event):
        """Handle window dragging"""
        if hasattr(self, '_drag_data'):
            dx = event.x - self._drag_data['x']
            dy = event.y - self._drag_data['y']
            self.geometry(f'+{self.winfo_x() + dx}+{self.winfo_y() + dy}')
            
    def show(self):
        """Show the bar with animation"""
        try:
            self.logger.info("Showing WaveformBar")
            
            # Position window at bottom center of screen
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            x = (screen_width - 120) // 2
            y = screen_height - 100  # 100 pixels from bottom
            
            self.geometry(f'120x20+{x}+{y}')
            self.deiconify()
            self.lift()  # Bring window to front
            self.attributes('-topmost', True)  # Ensure window stays on top
            self.update()  # Force window update
            
            self.start_animation()
            self.logger.info(f"WaveformBar shown at position ({x}, {y})")
        except Exception as e:
            self.logger.error(f"Error showing WaveformBar: {e}")
            self.logger.error(traceback.format_exc())
            
    def hide(self):
        """Hide the bar and stop animation"""
        try:
            self.logger.info("Hiding WaveformBar")
            self.stop_animation()
            self.withdraw()
            self.logger.info("WaveformBar hidden")
        except Exception as e:
            self.logger.error(f"Error hiding WaveformBar: {e}")
            self.logger.error(traceback.format_exc())
            
    def start_animation(self):
        """Start the waveform animation"""
        try:
            if not self.is_listening:
                self.is_listening = True
                self.logger.info("Starting waveform animation")
                self._animate_waveform()
        except Exception as e:
            self.logger.error(f"Error starting animation: {e}")
            self.logger.error(traceback.format_exc())
            
    def stop_animation(self):
        """Stop the waveform animation"""
        try:
            self.is_listening = False
            if self.animation_id:
                self.after_cancel(self.animation_id)
                self.animation_id = None
            self.logger.info("Stopped waveform animation")
        except Exception as e:
            self.logger.error(f"Error stopping animation: {e}")
            self.logger.error(traceback.format_exc())
            
    def _animate_waveform(self):
        """Animate the waveform"""
        try:
            if not self.is_listening:
                return
                
            # Update points with smooth transitions
            for i in range(len(self.points)):
                target = random.uniform(-5, 5)
                self.points[i] += (target - self.points[i]) * 0.3
                
            # Clear previous waveform
            self.canvas.delete('waveform')
            
            # Draw new waveform
            x_step = 120 / (len(self.points) - 1)
            coords = []
            
            # Create smooth curve through points
            for i in range(len(self.points)):
                x = i * x_step
                y = 10 + self.points[i]  # Center line at 10 (half of 20px height)
                coords.extend([x, y])
                
            if len(coords) >= 4:
                self.canvas.create_line(
                    coords,
                    fill='#4CAF50',
                    width=2,
                    smooth=True,
                    tags='waveform'
                )
                
            # Schedule next animation frame
            self.animation_id = self.after(50, self._animate_waveform)
            
        except Exception as e:
            self.logger.error(f"Error in waveform animation: {e}")
            self.logger.error(traceback.format_exc()) 