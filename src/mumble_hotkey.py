#!/usr/bin/env python3
"""
Mumble Hotkey - A speech-to-text application with hotkey support
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

# Configure pyautogui for safety and performance
pyautogui.FAILSAFE = True  # Move mouse to upper-left corner to abort
pyautogui.PAUSE = 0.1  # Add small pause between actions

# Import platform-specific modules
PLATFORM = platform.system().lower()
if PLATFORM == "windows":
    import winsound
elif PLATFORM == "darwin":  # macOS
    # No specific imports needed for sound on Mac
    pass
elif PLATFORM == "linux":
    # No specific imports needed for sound on Linux
    pass


class MumbleHotkey:
    """Main class for Mumble hotkey functionality"""
    
    def __init__(self):
        """Initialize the hotkey functionality"""
        # Set up the recognizer
        self.recognizer = sr.Recognizer()
        
        # Initialize state variables
        self.is_recording = False
        self.audio = None
        self.should_exit = False
        self.recording_start_time = 0
        
        # Load configuration
        self.config = self.load_config()
        
        # Configure hotkeys from config
        self.start_hotkey = self.config.get('hotkeys', 'start_hotkey', fallback='ctrl+space')
        self.stop_key = self.config.get('hotkeys', 'stop_key', fallback='space')
        
        # Sound settings
        self.enable_sounds = self.config.getboolean('sound', 'enable_sounds', fallback=True)
        self.start_frequency = self.config.getint('sound', 'start_frequency', fallback=880)
        self.start_duration = self.config.getint('sound', 'start_duration', fallback=200)
        self.stop_frequency = self.config.getint('sound', 'stop_frequency', fallback=440)
        self.stop_duration = self.config.getint('sound', 'stop_duration', fallback=200)
        
        # Behavior settings
        self.max_recording_time = self.config.getint('behavior', 'max_recording_time', fallback=60)
        
        # Platform-specific configurations
        if PLATFORM == "darwin" and self.start_hotkey == "ctrl+space":  # macOS
            self.start_hotkey = "command+space"
            print("Note: On macOS, using Command+Space instead of Ctrl+Space")
        
        # Print welcome message
        self.print_welcome()
    
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
        
        return config
    
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
            
        print(f"  3. Press {self.stop_key} (without modifier key) to stop and insert text")
        print("  4. Press Ctrl+C to exit")
        
        if self.max_recording_time > 0:
            print(f"\nMaximum recording time: {self.max_recording_time} seconds")
        
        if PLATFORM == "linux":
            print("\nNote: On Linux, you may need to run this script with sudo for keyboard access")
            
        print("\nStatus: Ready - Waiting for hotkey...\n")
    
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
    
    def start_recording(self):
        """Start the speech recognition process"""
        if not self.is_recording:
            self.is_recording = True
            self.recording_start_time = time.time()
            print("\nStarting recording... Speak now!")
            
            # Play start sound
            self.play_sound(self.start_frequency, self.start_duration)
            
            try:
                with sr.Microphone() as source:
                    # Adjust for ambient noise
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    # Listen to the microphone
                    self.audio = self.recognizer.listen(source, phrase_time_limit=None)
            except Exception as e:
                print(f"Error initializing microphone: {e}")
                self.is_recording = False
    
    def stop_recording_and_insert(self):
        """Stop recording, transcribe audio, and insert text"""
        if self.is_recording and self.audio:
            self.is_recording = False
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
    
    def run(self):
        """Main loop to monitor hotkeys and manage recording state"""
        try:
            while not self.should_exit:
                # Check if hotkey is held to start recording
                if keyboard.is_pressed(self.start_hotkey) and not self.is_recording:
                    self.start_recording()
                    # Small delay to avoid multiple triggers
                    time.sleep(0.2)
                
                # Check if Space is pressed (without modifier) to stop recording
                elif (self.is_recording and 
                      keyboard.is_pressed(self.stop_key) and 
                      not keyboard.is_pressed("ctrl") and
                      not (PLATFORM == "darwin" and keyboard.is_pressed("command"))):
                    self.stop_recording_and_insert()
                    # Small delay to avoid multiple triggers
                    time.sleep(0.2)
                
                # Check if maximum recording time has been reached
                elif self.is_recording and self.check_max_recording_time():
                    self.stop_recording_and_insert()
                
                # Small delay to reduce CPU usage
                time.sleep(0.01)
                
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