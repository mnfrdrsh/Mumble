#!/usr/bin/env python3
"""
Mumble Hotkey - A speech-to-text application with hotkey support and visual feedback
"""

import os
import sys
import time
import threading
import platform
import configparser
import speech_recognition as sr
import keyboard
import pyperclip
import pyautogui
import tkinter as tk
import math
from PIL import Image  # For the system tray icon
import pystray
from pystray import MenuItem as item

# Configure pyautogui for safety and performance
pyautogui.FAILSAFE = True  # Move mouse to upper-left corner to abort
pyautogui.PAUSE = 0.1  # Add small pause between actions

# Import platform-specific modules
PLATFORM = platform.system().lower()
if PLATFORM == "windows":
    import winsound
elif PLATFORM == "darwin":  # macOS
    pass
elif PLATFORM == "linux":
    pass


class MumbleHotkey:
    """Main class for Mumble hotkey functionality with visual feedback"""
    
    def __init__(self):
        """Initialize the hotkey functionality and GUI"""
        # Set up the recognizer
        self.recognizer = sr.Recognizer()
        
        # Initialize state variables
        self.is_recording = False
        self.audio = None
        self.should_exit = False
        self.recording_start_time = 0
        
        # Load configuration
        self.config = self.load_config()
        
        # Configure hotkeys
        self.start_hotkey = 'ctrl+alt'
        self.stop_key = None
        
        # Sound settings
        self.enable_sounds = self.config.getboolean('sound', 'enable_sounds', fallback=True)
        self.start_frequency = self.config.getint('sound', 'start_frequency', fallback=880)
        self.start_duration = self.config.getint('sound', 'start_duration', fallback=200)
        self.stop_frequency = self.config.getint('sound', 'stop_frequency', fallback=440)
        self.stop_duration = self.config.getint('sound', 'stop_duration', fallback=200)
        
        # Behavior settings
        self.max_recording_time = self.config.getint('behavior', 'max_recording_time', fallback=60)
        
        # Set initial position from config or defaults
        self.bar_pos_x = self.config.getint('gui', 'bar_position_x', fallback=50)
        self.bar_pos_y = self.config.getint('gui', 'bar_position_y', fallback=50)
        
        # Get bar dimensions from config or use defaults
        self.bar_width = self.config.getint('gui', 'bar_width', fallback=120)
        self.bar_height = self.config.getint('gui', 'bar_height', fallback=20)
        
        # Initialize GUI for listening bar
        self.root = tk.Tk()
        self.root.title("Mumble")
        self.root.attributes("-topmost", True)  # Keep window on top
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.geometry(f"{self.bar_width}x{self.bar_height}+{self.bar_pos_x}+{self.bar_pos_y}")  # Position from config
        
        # Canvas for squiggly line animation
        self.canvas = tk.Canvas(self.root, width=self.bar_width, height=self.bar_height, bg="white", highlightthickness=0)
        self.canvas.pack()
        
        # Squiggly line properties
        self.line_id = None
        self.phase = 0  # For animation
        self.idle_color = "gray"
        self.active_color = "green"
        self.draw_squiggly_line()  # Draw initial idle line
        
        # Dragging variables
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # Bind mouse events for dragging
        self.canvas.bind("<Button-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag)
        
        # Start animation loop
        self.root.after(50, self.animate_squiggly_line)
        
        # Initialize system tray icon
        self.setup_tray()
        
        # Print welcome message
        self.print_welcome()
        
        # Bind closing event
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)
        
        # Start hotkey monitoring in a separate thread
        self.hotkey_thread = threading.Thread(target=self.monitor_hotkeys, daemon=True)
        self.hotkey_thread.start()

    def load_config(self):
        """Load configuration from config.ini file"""
        config = configparser.ConfigParser()
        
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, "config.ini")
        
        # Check if config file exists
        if os.path.exists(config_path):
            try:
                config.read(config_path)
                print(f"Loaded configuration from {config_path}")
            except Exception as e:
                print(f"Error loading configuration: {e}")
                # Use default configuration
        else:
            print("Configuration file not found, using defaults")
            # Create default sections
            config.add_section('hotkeys')
            config.add_section('sound')
            config.add_section('behavior')
        
        # Ensure GUI section exists
        if not config.has_section('gui'):
            config.add_section('gui')
            
        return config
    
    def save_config(self):
        """Save configuration to config.ini file"""
        # Update GUI position in config
        self.config.set('gui', 'bar_position_x', str(self.bar_pos_x))
        self.config.set('gui', 'bar_position_y', str(self.bar_pos_y))
        self.config.set('gui', 'bar_width', str(self.bar_width))
        self.config.set('gui', 'bar_height', str(self.bar_height))
        
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, "config.ini")
        
        # Write to file
        with open(config_path, 'w') as configfile:
            self.config.write(configfile)
    
    def start_drag(self, event):
        """Start dragging the listening bar"""
        # Store initial mouse position
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root
    
    def on_drag(self, event):
        """Update position while dragging"""
        # Update position based on mouse movement
        delta_x = event.x_root - self.drag_start_x
        delta_y = event.y_root - self.drag_start_y
        self.bar_pos_x = self.root.winfo_x() + delta_x
        self.bar_pos_y = self.root.winfo_y() + delta_y
        self.root.geometry(f"+{self.bar_pos_x}+{self.bar_pos_y}")
        # Reset starting position
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root
    
    def stop_drag(self, event):
        """Stop dragging and save position"""
        # Save position to config
        self.save_config()
        print(f"Listening bar pinned to ({self.bar_pos_x}, {self.bar_pos_y})")
    
    def print_welcome(self):
        """Print welcome message and instructions"""
        print("\n" + "="*60)
        print("Mumble Hotkey Mode".center(60))
        print("="*60)
        print("\nInstructions:")
        
        # Platform-specific instructions
        if PLATFORM == "darwin":  # macOS
            print(f"  1. Hold {self.start_hotkey} to start recording")
            print(f"  2. Release {self.start_hotkey} to continue recording")
        else:
            print(f"  1. Hold {self.start_hotkey} to start recording")
            print(f"  2. Release {self.start_hotkey} to continue recording")
            
        print(f"  3. Release either Ctrl or Alt to stop and insert text")
        print("  4. Press Ctrl+C or close the tray icon to exit")
        
        if self.max_recording_time > 0:
            print(f"\nMaximum recording time: {self.max_recording_time} seconds")
        
        if PLATFORM == "linux":
            print("\nNote: On Linux, you may need to run this script with sudo for keyboard access")
            
        print("\nStatus: Ready - Waiting for hotkey...\n")
        print("A small listening bar should be visible on your screen.")
        print("You can drag the listening bar to reposition it.")

    def play_sound(self, frequency, duration):
        """Play a notification sound based on platform"""
        if not self.enable_sounds:
            return
            
        try:
            if PLATFORM == "windows":
                winsound.Beep(frequency, duration)
            elif PLATFORM == "darwin":  # macOS
                os.system(f"afplay /System/Library/Sounds/Tink.aiff")
            elif PLATFORM == "linux":
                os.system(f"echo -e '\a'")  # Terminal bell
        except:
            # If sound fails, just pass
            pass
    
    def setup_tray(self):
        """Set up the system tray icon"""
        # Create a simple square image for the icon
        image = Image.new('RGB', (64, 64), color='green')
        
        # Create the system tray icon
        menu = (
            item('Status: Ready', lambda: None, enabled=False),
            item('Exit', self.exit_app)
        )
        
        self.tray_icon = pystray.Icon(
            "mumble_hotkey",
            image,
            "Mumble Hotkey",
            menu
        )
        
        # Start the icon in a separate thread
        threading.Thread(target=self.tray_icon.run, daemon=True).start()
    
    def update_tray_status(self, is_recording):
        """Update the system tray icon status"""
        if is_recording:
            # Create red icon for recording
            image = Image.new('RGB', (64, 64), color='red')
            self.tray_icon.icon = image
            self.tray_icon.menu = (
                item('Status: Recording...', lambda: None, enabled=False),
                item('Exit', self.exit_app)
            )
        else:
            # Create green icon for ready
            image = Image.new('RGB', (64, 64), color='green')
            self.tray_icon.icon = image
            self.tray_icon.menu = (
                item('Status: Ready', lambda: None, enabled=False),
                item('Exit', self.exit_app)
            )
    
    def draw_squiggly_line(self):
        """Draws or updates the squiggly line on the canvas."""
        self.canvas.delete("all")  # Clear previous line
        points = []
        width = self.bar_width
        height = self.bar_height
        amplitude = 5  # Height of waves (reduced from 10)
        frequency = 0.15  # Wave frequency (increased for more waves in smaller space)

        for x in range(0, width, 2):
            if self.is_recording:
                # Animate during recording
                y = height / 2 + amplitude * math.sin(frequency * x + self.phase)
            else:
                # Static idle line
                y = height / 2 + amplitude * math.sin(frequency * x)
            points.extend([x, y])

        color = self.active_color if self.is_recording else self.idle_color
        self.line_id = self.canvas.create_line(points, fill=color, width=1, smooth=True)  # Reduced line width from 2 to 1

    def animate_squiggly_line(self):
        """Updates the phase for the squiggly line animation."""
        if self.is_recording:
            self.phase += 0.2  # Adjust speed of animation
            self.draw_squiggly_line()
        self.root.after(50, self.animate_squiggly_line)  # Continue animation

    def exit_app(self):
        """Clean exit of the application"""
        self.should_exit = True
        self.tray_icon.stop()
        self.root.destroy()  # Close the GUI window
    
    def start_recording(self):
        """Start the speech recognition process"""
        if not self.is_recording:
            self.is_recording = True
            self.update_tray_status(True)
            self.recording_start_time = time.time()
            print("\nStarting recording... Speak now!")
            
            # Play start sound
            self.play_sound(self.start_frequency, self.start_duration)
            
            # Start a new thread for audio processing
            threading.Thread(target=self.process_audio).start()
            
            # Update squiggly line
            self.draw_squiggly_line()

    def process_audio(self):
        """Capture and process audio in a separate thread"""
        try:
            with sr.Microphone() as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # Listen to the microphone
                self.audio = self.recognizer.listen(source, phrase_time_limit=None)
                self.stop_recording_and_insert()  # Process after capturing
        except Exception as e:
            print(f"Error initializing microphone: {e}")
            self.is_recording = False
            self.update_tray_status(False)
            self.draw_squiggly_line()  # Update squiggly line on error
    
    def stop_recording_and_insert(self):
        """Stop recording, transcribe audio, and insert text"""
        if self.is_recording and self.audio:
            self.is_recording = False
            self.update_tray_status(False)
            print("Stopping recording... Processing speech...")
            
            # Play stop sound
            self.play_sound(self.stop_frequency, self.stop_duration)
            
            try:
                # Transcribe audio using Google Speech Recognition
                text = self.recognizer.recognize_google(self.audio)
                print(f"Transcribed: \"{text}\"")
                
                # Insert text into active application
                self.insert_text(text)
                
                # Reset audio
                self.audio = None
                
            except sr.UnknownValueError:
                print("Could not understand audio. Please try again.")
            except sr.RequestError as e:
                print(f"Error with the speech recognition service: {e}")
            except Exception as e:
                print(f"Error processing speech: {e}")
            finally:
                self.draw_squiggly_line()  # Update squiggly line
    
    def insert_text(self, text):
        """Insert transcribed text into active application"""
        if text:
            try:
                # Copy text to clipboard
                pyperclip.copy(text)
                
                # Simulate paste shortcut based on platform
                if PLATFORM == "darwin":  # macOS
                    pyautogui.hotkey("command", "v")
                else:
                    pyautogui.hotkey("ctrl", "v")
                    
                print("Text inserted into active application.")
            except Exception as e:
                print(f"Error inserting text: {e}")
                print("Text was copied to clipboard. You can manually paste it.")
    
    def check_max_recording_time(self):
        """Check if maximum recording time has been reached"""
        if self.max_recording_time <= 0:
            return False  # No time limit
            
        elapsed_time = time.time() - self.recording_start_time
        if elapsed_time >= self.max_recording_time:
            print(f"\nMaximum recording time of {self.max_recording_time} seconds reached.")
            return True
        return False
    
    def monitor_hotkeys(self):
        """Monitor hotkeys in a separate thread"""
        while not self.should_exit:
            # Check if both Ctrl and Alt are held to start recording
            if keyboard.is_pressed("ctrl") and keyboard.is_pressed("alt") and not self.is_recording:
                self.start_recording()
                time.sleep(0.2)  # Debounce to avoid multiple triggers
            
            # Check if either Ctrl or Alt is released to stop recording
            elif self.is_recording and (not keyboard.is_pressed("ctrl") or not keyboard.is_pressed("alt")):
                self.stop_recording_and_insert()
                time.sleep(0.2)  # Debounce to avoid multiple triggers
            
            # Check maximum recording time
            if self.is_recording and self.check_max_recording_time():
                self.stop_recording_and_insert()
            
            time.sleep(0.01)  # Reduce CPU usage
    
    def run(self):
        """Main loop to run the application"""
        try:
            # Run the Tkinter main loop
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nExiting Mumble Hotkey Mode...")
        finally:
            self.should_exit = True
            print("Mumble Hotkey Mode closed.")


def main():
    """Main entry point for the application"""
    try:
        # Check for platform-specific requirements
        if PLATFORM == "linux":
            print("Note: On Linux, keyboard monitoring may require root privileges.")
            print("If the hotkeys don't work, try running with sudo.")
            
        app = MumbleHotkey()
        app.run()
    except Exception as e:
        print(f"Error running Mumble Hotkey: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()