"""
Enhanced pill-shaped bar UI for Mumble Quick using Tkinter
Modern styling and improved functionality while maintaining Tkinter compatibility
"""

import tkinter as tk
import math
import random
from typing import List, Optional
import logging
import traceback


class EnhancedWaveformBar(tk.Tk):
    """An enhanced pill-shaped bar with modern styling and improved animations"""
    
    def __init__(self):
        try:
            super().__init__()
            self.logger = logging.getLogger('mumble.quick.ui')
            self.logger.info("Initializing Enhanced WaveformBar")
            
            # Configure window with modern settings
            self.overrideredirect(True)  # Remove window decorations
            self.attributes('-topmost', True)  # Keep window on top
            self.attributes('-alpha', 0.95)  # Slight transparency for modern look
            
            # Try to make window stay above other windows on Windows
            try:
                self.wm_attributes('-topmost', True)
                self.lift()
            except:
                pass
            
            # Enhanced color scheme
            self.colors = {
                'bg': '#1e1e1e',           # Darker background
                'border': '#404040',        # Lighter border
                'waveform': '#00d4aa',      # Modern cyan-green
                'close': '#ff6b6b',         # Modern red
                'text': '#ffffff'           # White text
            }
            
            self.configure(bg=self.colors['bg'])
            
            # Set window size with better proportions
            self.width = 140
            self.height = 24
            self.geometry(f'{self.width}x{self.height}')
            
            # Create main frame with padding
            self.main_frame = tk.Frame(
                self,
                bg=self.colors['bg'],
                highlightthickness=0
            )
            self.main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
            
            # Create canvas for waveform with better size
            self.canvas = tk.Canvas(
                self.main_frame,
                width=self.width-4,
                height=self.height-4,
                bg=self.colors['bg'],
                highlightthickness=0,
                bd=0
            )
            self.canvas.pack(fill=tk.BOTH, expand=True)
            
            # Initialize enhanced waveform variables
            self.points: List[float] = [0.0] * 25  # More points for smoother animation
            self.is_listening = False
            self.animation_id: Optional[str] = None
            self.animation_speed = 40  # Faster animation (lower = faster)
            
            # Enhanced visual elements
            self._create_modern_pill_shape()
            self._add_modern_close_button()
            self._enable_smooth_drag()
            
            # Add fade in/out effects
            self.fade_steps = 10
            self.current_alpha = 0.0
            
            self.logger.info("Enhanced WaveformBar initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing Enhanced WaveformBar: {e}")
            self.logger.error(traceback.format_exc())
            raise
    
    def _create_modern_pill_shape(self):
        """Create a modern pill shape with enhanced styling"""
        try:
            def _create_rounded_rect():
                radius = 12  # Larger radius for more modern look
                points = []
                
                # Create smoother curves with more points
                for i in range(0, 90, 10):  # Top-right curve
                    x = (self.width-4) - radius + radius * math.cos(math.radians(i))
                    y = radius - radius * math.sin(math.radians(i))
                    points.extend([x, y])
                
                for i in range(90, 180, 10):  # Top-left curve
                    x = radius + radius * math.cos(math.radians(i))
                    y = radius - radius * math.sin(math.radians(i))
                    points.extend([x, y])
                
                for i in range(180, 270, 10):  # Bottom-left curve
                    x = radius + radius * math.cos(math.radians(i))
                    y = (self.height-4) - radius - radius * math.sin(math.radians(i))
                    points.extend([x, y])
                
                for i in range(270, 360, 10):  # Bottom-right curve
                    x = (self.width-4) - radius + radius * math.cos(math.radians(i))
                    y = (self.height-4) - radius - radius * math.sin(math.radians(i))
                    points.extend([x, y])
                
                return points
            
            # Create background with gradient effect (simulated)
            self.bg_shape = self.canvas.create_polygon(
                _create_rounded_rect(),
                smooth=True,
                fill=self.colors['bg'],
                outline=self.colors['border'],
                width=2
            )
            
            # Add inner shadow effect
            inner_points = []
            radius = 10
            for i in range(0, 360, 15):
                x = (self.width-4)/2 + (radius-2) * math.cos(math.radians(i))
                y = (self.height-4)/2 + (radius-2) * math.sin(math.radians(i))
                inner_points.extend([x, y])
            
            self.inner_shadow = self.canvas.create_polygon(
                inner_points,
                smooth=True,
                fill='',
                outline='#2a2a2a',
                width=1
            )
            
            self.logger.info("Modern pill shape created")
        except Exception as e:
            self.logger.error(f"Error creating modern pill shape: {e}")
            self.logger.error(traceback.format_exc())
    
    def _add_modern_close_button(self):
        """Add a modern close button with hover effects"""
        size = 16
        padding = 6
        x = self.width - size - padding
        y = padding
        
        # Create close button with modern styling
        self.close_button = self.canvas.create_oval(
            x-2, y-2, x+size+2, y+size+2,
            fill=self.colors['bg'],
            outline=self.colors['close'],
            width=1
        )
        
        self.close_text = self.canvas.create_text(
            x+size//2, y+size//2,
            text='×',
            fill=self.colors['close'],
            font=('Arial', 10, 'bold')
        )
        
        # Bind hover events for modern interaction
        self.canvas.tag_bind(self.close_button, '<Enter>', self._on_close_hover)
        self.canvas.tag_bind(self.close_text, '<Enter>', self._on_close_hover)
        self.canvas.tag_bind(self.close_button, '<Leave>', self._on_close_leave)
        self.canvas.tag_bind(self.close_text, '<Leave>', self._on_close_leave)
        self.canvas.tag_bind(self.close_button, '<Button-1>', lambda e: self.quit())
        self.canvas.tag_bind(self.close_text, '<Button-1>', lambda e: self.quit())
    
    def _on_close_hover(self, event):
        """Handle close button hover"""
        self.canvas.itemconfig(self.close_button, fill=self.colors['close'])
        self.canvas.itemconfig(self.close_text, fill='white')
    
    def _on_close_leave(self, event):
        """Handle close button leave"""
        self.canvas.itemconfig(self.close_button, fill=self.colors['bg'])
        self.canvas.itemconfig(self.close_text, fill=self.colors['close'])
    
    def _enable_smooth_drag(self):
        """Enable smooth window dragging with momentum"""
        self.bind('<Button-1>', self._on_drag_start)
        self.bind('<B1-Motion>', self._on_drag_motion)
        self.bind('<ButtonRelease-1>', self._on_drag_end)
        
        self.canvas.bind('<Button-1>', self._on_drag_start)
        self.canvas.bind('<B1-Motion>', self._on_drag_motion)
        self.canvas.bind('<ButtonRelease-1>', self._on_drag_end)
        
        self._drag_data = {'x': 0, 'y': 0, 'start_time': 0}
    
    def _on_drag_start(self, event):
        """Store initial position for smooth dragging"""
        import time
        self._drag_data = {
            'x': event.x,
            'y': event.y,
            'start_time': time.time()
        }
    
    def _on_drag_motion(self, event):
        """Handle smooth window dragging"""
        if hasattr(self, '_drag_data'):
            dx = event.x - self._drag_data['x']
            dy = event.y - self._drag_data['y']
            
            new_x = self.winfo_x() + dx
            new_y = self.winfo_y() + dy
            
            # Add boundary constraints
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            
            new_x = max(0, min(new_x, screen_width - self.width))
            new_y = max(0, min(new_y, screen_height - self.height))
            
            self.geometry(f'+{new_x}+{new_y}')
    
    def _on_drag_end(self, event):
        """Handle end of dragging"""
        pass
    
    def show_with_fade(self):
        """Show the bar with a smooth fade-in animation"""
        try:
            self.logger.info("Showing Enhanced WaveformBar with fade")
            
            # Position window at bottom center of screen
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            x = (screen_width - self.width) // 2
            y = screen_height - 120  # A bit higher for better visibility
            
            self.geometry(f'{self.width}x{self.height}+{x}+{y}')
            self.deiconify()
            
            # Start fade-in animation
            self.current_alpha = 0.0
            self._fade_in()
            
            self.start_animation()
            self.logger.info(f"Enhanced WaveformBar shown at position ({x}, {y})")
        except Exception as e:
            self.logger.error(f"Error showing Enhanced WaveformBar: {e}")
            self.logger.error(traceback.format_exc())
    
    def _fade_in(self):
        """Smooth fade-in animation"""
        try:
            if self.current_alpha < 0.95:
                self.current_alpha += 0.95 / self.fade_steps
                self.attributes('-alpha', self.current_alpha)
                self.after(30, self._fade_in)
            else:
                self.attributes('-alpha', 0.95)
        except Exception as e:
            self.logger.error(f"Error in fade-in: {e}")
    
    def hide_with_fade(self):
        """Hide the bar with a smooth fade-out animation"""
        try:
            self.logger.info("Hiding Enhanced WaveformBar with fade")
            self.stop_animation()
            self.current_alpha = 0.95
            self._fade_out()
        except Exception as e:
            self.logger.error(f"Error hiding Enhanced WaveformBar: {e}")
            self.logger.error(traceback.format_exc())
    
    def _fade_out(self):
        """Smooth fade-out animation"""
        try:
            if self.current_alpha > 0.1:
                self.current_alpha -= 0.95 / self.fade_steps
                self.attributes('-alpha', self.current_alpha)
                self.after(30, self._fade_out)
            else:
                self.withdraw()
                self.attributes('-alpha', 0.95)  # Reset for next show
        except Exception as e:
            self.logger.error(f"Error in fade-out: {e}")
    
    def show(self):
        """Enhanced show method"""
        self.show_with_fade()
    
    def hide(self):
        """Enhanced hide method"""
        self.hide_with_fade()
    
    def start_animation(self):
        """Start the enhanced waveform animation"""
        try:
            if not self.is_listening:
                self.is_listening = True
                self.logger.info("Starting enhanced waveform animation")
                self._animate_enhanced_waveform()
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
            self.logger.info("Stopped enhanced waveform animation")
        except Exception as e:
            self.logger.error(f"Error stopping animation: {e}")
            self.logger.error(traceback.format_exc())
    
    def _animate_enhanced_waveform(self):
        """Enhanced waveform animation with better visual effects"""
        try:
            if not self.is_listening:
                return
            
            # Update points with more sophisticated animation
            for i in range(len(self.points)):
                # Create wave patterns that flow
                wave_offset = (i * 0.5) + (random.random() * 0.3)
                base_amplitude = 3.0 + math.sin(wave_offset) * 2.0
                target = random.uniform(-base_amplitude, base_amplitude)
                
                # Smoother interpolation
                self.points[i] += (target - self.points[i]) * 0.25
            
            # Clear previous waveform
            self.canvas.delete('waveform')
            
            # Draw enhanced waveform with gradient-like effect
            self._draw_enhanced_waveform()
            
            # Schedule next animation frame
            self.animation_id = self.after(self.animation_speed, self._animate_enhanced_waveform)
            
        except Exception as e:
            self.logger.error(f"Error in enhanced waveform animation: {e}")
            self.logger.error(traceback.format_exc())
    
    def _draw_enhanced_waveform(self):
        """Draw the enhanced waveform with multiple layers"""
        try:
            center_y = (self.height - 4) / 2
            x_step = (self.width - 40) / (len(self.points) - 1)  # Leave space for close button
            
            # Draw main waveform
            coords = []
            for i in range(len(self.points)):
                x = 20 + i * x_step  # Start offset for padding
                y = center_y + self.points[i]
                coords.extend([x, y])
            
            if len(coords) >= 4:
                # Main waveform line
                self.canvas.create_line(
                    coords,
                    fill=self.colors['waveform'],
                    width=3,
                    smooth=True,
                    tags='waveform',
                    capstyle=tk.ROUND
                )
                
                # Add glow effect with multiple lighter lines
                for width, alpha in [(5, 0.3), (7, 0.15)]:
                    glow_color = self._blend_color(self.colors['waveform'], self.colors['bg'], alpha)
                    self.canvas.create_line(
                        coords,
                        fill=glow_color,
                        width=width,
                        smooth=True,
                        tags='waveform',
                        capstyle=tk.ROUND
                    )
            
        except Exception as e:
            self.logger.error(f"Error drawing enhanced waveform: {e}")
            self.logger.error(traceback.format_exc())
    
    def _blend_color(self, color1, color2, alpha):
        """Blend two colors for glow effects"""
        try:
            # Simple color blending
            if color1.startswith('#') and color2.startswith('#'):
                r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
                r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
                
                r = int(r1 * alpha + r2 * (1 - alpha))
                g = int(g1 * alpha + g2 * (1 - alpha))
                b = int(b1 * alpha + b2 * (1 - alpha))
                
                return f'#{r:02x}{g:02x}{b:02x}'
            return color1
        except:
            return color1


# Test the enhanced waveform bar
if __name__ == '__main__':
    import time
    
    # Create and test the enhanced bar
    bar = EnhancedWaveformBar()
    bar.show()
    bar.start_animation()
    
    # Keep it running for testing
    bar.mainloop() 