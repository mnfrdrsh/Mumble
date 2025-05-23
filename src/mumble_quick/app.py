"""
Main application module for Mumble Quick
"""

import os
import sys
import keyboard
import pyperclip
import pyautogui
from threading import Thread
import logging
import traceback

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.speech_recognition import SpeechRecognizer
from shared.logging import setup_logging
from ui.pill_bar import WaveformBar

class MumbleQuick:
    """Main application class for Mumble Quick"""
    
    def __init__(self):
        """Initialize the application"""
        try:
            self.logger = setup_logging('quick')
            self.logger.info("Initializing Mumble Quick...")
            
            self.recognizer = SpeechRecognizer()
            self.logger.info("Speech recognizer initialized")
            
            self.ui = WaveformBar()
            self.ui.withdraw()  # Hide window initially
            self.logger.info("UI initialized and hidden")
            
            self.recognition_thread = None
            
            # Set up hotkey - using a more specific combination
            try:
                # Try primary hotkey first (just Ctrl+Alt instead of Ctrl+Alt+M)
                keyboard.add_hotkey('ctrl+alt', self.toggle_listening, suppress=True)
                self.logger.info("Primary hotkey (Ctrl+Alt) registered successfully")
            except Exception as primary_error:
                self.logger.warning(f"Failed to register primary hotkey: {primary_error}")
                try:
                    # Fallback to secondary hotkey (Ctrl+Shift)
                    keyboard.add_hotkey('ctrl+shift', self.toggle_listening, suppress=True)
                    self.logger.info("Secondary hotkey (Ctrl+Shift) registered successfully")
                except Exception as secondary_error:
                    self.logger.error(f"Failed to register secondary hotkey: {secondary_error}")
                    self.logger.error(traceback.format_exc())
                    raise
                
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            self.logger.error(traceback.format_exc())
            raise
            
    def toggle_listening(self):
        """Toggle speech recognition on/off"""
        try:
            self.logger.info("Toggle listening called")
            if not self.recognizer.is_listening:
                self.start_listening()
            else:
                self.stop_listening()
        except Exception as e:
            self.logger.error(f"Error in toggle_listening: {e}")
            self.logger.error(traceback.format_exc())
            
    def start_listening(self):
        """Start speech recognition"""
        try:
            self.logger.info("Starting listening...")
            if self.recognition_thread and self.recognition_thread.is_alive():
                self.logger.info("Recognition thread already running")
                return
                
            # Show UI
            self.ui.show()  # This now includes deiconify and other visibility settings
            self.logger.info("UI shown")
            
            # Start recognition in a separate thread
            self.recognition_thread = Thread(
                target=self.recognizer.start_listening,
                args=(self.on_transcription,),
                daemon=True
            )
            self.recognition_thread.start()
            self.logger.info("Recognition thread started")
            
        except Exception as e:
            self.logger.error(f"Error in start_listening: {e}")
            self.logger.error(traceback.format_exc())
            
    def stop_listening(self):
        """Stop speech recognition"""
        try:
            self.logger.info("Stopping listening...")
            self.recognizer.stop_listening()
            self.ui.hide()
            self.logger.info("Listening stopped")
        except Exception as e:
            self.logger.error(f"Error in stop_listening: {e}")
            self.logger.error(traceback.format_exc())
            
    def on_transcription(self, text: str):
        """Handle transcribed text"""
        try:
            if text:
                self.logger.info(f"Received transcription: {text}")
                # Type the text at current cursor position
                pyperclip.copy(text)
                pyautogui.hotkey('ctrl', 'v')
                self.logger.info("Text inserted successfully")
        except Exception as e:
            self.logger.error(f"Error in on_transcription: {e}")
            self.logger.error(traceback.format_exc())
            
    def run(self):
        """Run the application"""
        try:
            self.logger.info("Starting Mumble Quick application")
            print("Mumble Quick is running.")
            print("Press Ctrl+Alt (or Ctrl+Shift) to start/stop speech recognition.")
            print("Check the logs directory for detailed information.")
            self.ui.mainloop()
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
            self.logger.error(traceback.format_exc())
        finally:
            self.logger.info("Shutting down Mumble Quick")
            self.stop_listening()
            
if __name__ == '__main__':
    try:
        app = MumbleQuick()
        app.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        print("Check the logs directory for detailed information.")
        sys.exit(1) 