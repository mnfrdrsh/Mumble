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
            
            # Configure window with improved settings for visibility
            self.overrideredirect(True)  # Remove window decorations
            self.attributes('-topmost', True)  # Keep window on top
            self.configure(bg='#2C2C2C')
            
            # IMPROVED: Set window size and ensure it's visible
            self.width = 120
            self.height = 20
            self.geometry(f'{self.width}x{self.height}')
            
            # IMPROVED: Force window to be visible initially (hidden later)
            self.withdraw()  # Start hidden, will be shown on demand
            
            # Create canvas for waveform
            self.canvas = tk.Canvas(
                self,
                width=self.width,
                height=self.height,
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
                    self.width - radius, 0,  # Top right
                    self.width, radius,  # Right top
                    self.width, self.height - radius,  # Right bottom
                    self.width - radius, self.height,  # Bottom right
                    radius, self.height,  # Bottom left
                    0, self.height - radius,  # Left bottom
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
        close_frame.place(x=self.width-size-padding, y=padding)
        
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
        """Show the bar with animation - IMPROVED VERSION"""
        try:
            self.logger.info("Showing WaveformBar - Starting show process")
            
            # IMPROVED: Get screen dimensions more reliably
            self.update_idletasks()  # Ensure window is ready
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            
            # IMPROVED: Calculate position with better bounds checking
            x = max(0, (screen_width - self.width) // 2)
            y = max(0, screen_height - 150)  # Higher up for better visibility
            
            self.logger.info(f"Screen size: {screen_width}x{screen_height}")
            self.logger.info(f"Calculated position: ({x}, {y})")
            
            # IMPROVED: Set geometry first, then show
            self.geometry(f'{self.width}x{self.height}+{x}+{y}')
            
            # IMPROVED: Force window to be visible with multiple methods
            self.deiconify()  # Make window visible
            self.update()     # Process pending events
            self.lift()       # Bring to front
            self.focus_force()  # Force focus (may help with visibility)
            self.attributes('-topmost', True)  # Ensure it stays on top
            
            # IMPROVED: Additional visibility checks
            if self.winfo_viewable():
                self.logger.info("Window is viewable")
            else:
                self.logger.warning("Window is NOT viewable - forcing visibility")
                self.tkraise()  # Alternative method to bring to front
            
            # Start animation
            self.start_animation()
            
            # IMPROVED: Log final position for debugging
            actual_x = self.winfo_x()
            actual_y = self.winfo_y()
            self.logger.info(f"WaveformBar shown at actual position ({actual_x}, {actual_y})")
            self.logger.info(f"Window dimensions: {self.winfo_width()}x{self.winfo_height()}")
            
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
            x_step = self.width / (len(self.points) - 1)
            coords = []
            
            # Create smooth curve through points
            for i in range(len(self.points)):
                x = i * x_step
                y = (self.height / 2) + self.points[i]  # Center line
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


# Test the waveform bar if run directly
if __name__ == '__main__':
    import sys
    
    # Create and test the waveform bar
    bar = WaveformBar()
    print("WaveformBar created - showing...")
    bar.show()
    print("WaveformBar shown - starting animation...")
    bar.start_animation()
    
    # Keep it running for testing
    print("Press Ctrl+C to exit or close the window")
    try:
        bar.mainloop()
    except KeyboardInterrupt:
        print("Exiting...")
        bar.destroy() 