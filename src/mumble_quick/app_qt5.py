"""
Main application module for Mumble Quick using PyQt5
Modern Qt-based replacement for the Tkinter implementation
"""

import os
import sys
import keyboard
import pyperclip
import pyautogui
from threading import Thread
import logging
import traceback

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.adaptive_speech import create_adaptive_speech_recognizer
from shared.logging import setup_logging
from ui.pill_bar_qt5 import WaveformBar


class MumbleQuickQt(QObject):
    """Main application class for Mumble Quick using PyQt5"""
    
    # Signal for transcription received
    transcription_received = pyqtSignal(str)
    
    def __init__(self):
        """Initialize the application"""
        super().__init__()
        try:
            self.logger = setup_logging('quick')
            self.logger.info("Initializing Mumble Quick (PyQt5)...")
            
            # Initialize Qt Application if not exists
            self.app = QApplication.instance()
            if self.app is None:
                self.app = QApplication(sys.argv)
                self.app.setQuitOnLastWindowClosed(False)  # Keep app running when UI hidden
            
            self.recognizer = create_adaptive_speech_recognizer()
            self.logger.info("Adaptive speech recognizer initialized")
            
            self.ui = WaveformBar()
            self.ui.close_requested.connect(self.stop_listening)
            self.ui.hide()  # Hide window initially
            self.logger.info("PyQt5 UI initialized and hidden")
            
            # Connect transcription signal
            self.transcription_received.connect(self.insert_text)
            
            self.recognition_thread = None
            
            # Set up hotkey - using a more specific combination
            try:
                # Try primary hotkey first (just Ctrl+Alt instead of Ctrl+Alt+M)
                keyboard.add_hotkey('ctrl+alt', self.on_hotkey_pressed, suppress=True)
                self.logger.info("Primary hotkey (Ctrl+Alt) registered successfully")
            except Exception as primary_error:
                self.logger.warning(f"Failed to register primary hotkey: {primary_error}")
                try:
                    # Fallback to secondary hotkey (Ctrl+Shift)
                    keyboard.add_hotkey('ctrl+shift', self.on_hotkey_pressed, suppress=True)
                    self.logger.info("Secondary hotkey (Ctrl+Shift) registered successfully")
                except Exception as secondary_error:
                    self.logger.error(f"Failed to register secondary hotkey: {secondary_error}")
                    self.logger.error(traceback.format_exc())
                    raise
                
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            self.logger.error(traceback.format_exc())
            raise
    
    def on_hotkey_pressed(self):
        """Handle hotkey press - toggle listening state"""
        try:
            self.logger.info("Hotkey pressed! Toggling listening...")
            
            # Use QTimer to ensure we're in the main Qt thread
            QTimer.singleShot(0, self.toggle_listening)
            
        except Exception as e:
            self.logger.error(f"Error in on_hotkey_pressed: {e}")
            self.logger.error(traceback.format_exc())
            
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
            self.ui.show()
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
        """Handle transcribed text - emit signal to main thread"""
        try:
            if text:
                self.logger.info(f"Received transcription: {text}")
                # Emit signal to be handled in main Qt thread
                self.transcription_received.emit(text)
        except Exception as e:
            self.logger.error(f"Error in on_transcription: {e}")
            self.logger.error(traceback.format_exc())
    
    def insert_text(self, text: str):
        """Insert text at current cursor position"""
        try:
            # Type the text at current cursor position
            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'v')
            self.logger.info("Text inserted successfully")
        except Exception as e:
            self.logger.error(f"Error inserting text: {e}")
            self.logger.error(traceback.format_exc())
            
    def run(self):
        """Run the application"""
        try:
            self.logger.info("Starting Mumble Quick (PyQt5) application")
            print("Mumble Quick (PyQt5) is running.")
            print("Press Ctrl+Alt (or Ctrl+Shift) to start/stop speech recognition.")
            print("Check the logs directory for detailed information.")
            
            # Set up periodic status check
            self.status_timer = QTimer()
            self.status_timer.timeout.connect(self.check_status)
            self.status_timer.start(5000)  # Check every 5 seconds
            
            # Run the Qt event loop
            return self.app.exec_()
            
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
            return 0
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
            self.logger.error(traceback.format_exc())
            return 1
        finally:
            self.logger.info("Shutting down Mumble Quick (PyQt5)")
            self.stop_listening()
    
    def check_status(self):
        """Periodically check status for debugging"""
        try:
            # This method helps us debug UI state
            self.logger.debug(f"Status check - is_listening: {self.recognizer.is_listening}")
        except Exception as e:
            self.logger.error(f"Error in check_status: {e}")


def main():
    """Main function to run the application"""
    try:
        app = MumbleQuickQt()
        exit_code = app.run()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Fatal error: {e}")
        print("Check the logs directory for detailed information.")
        sys.exit(1)


if __name__ == '__main__':
    main() 