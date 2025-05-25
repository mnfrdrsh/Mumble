"""
PyAudio-based speech recognizer for Mumble applications.
"""

import speech_recognition as sr
import logging
import threading
import time
from typing import Optional, Callable

from src.shared.base_audio_recognizer import BaseAudioRecognizer

class PyAudioRecognizer(BaseAudioRecognizer):
    """
    Speech recognizer implementation using PyAudio for audio input.

    This class handles capturing audio from the microphone via PyAudio
    and uses the base class to perform speech recognition.
    """

    def __init__(self):
        """Initialize the PyAudioRecognizer."""
        super().__init__(logger_name='mumble.pyaudio_speech')
        # self._is_listening_state is inherited and managed by superclass
        # self.dictation_timeout is inherited from superclass
        # self.recognizer is inherited from superclass
        
        self._stop_requested = threading.Event() # Use Event for clearer signaling
        self._listen_thread: Optional[threading.Thread] = None
        self._callback: Optional[Callable[[str], None]] = None

    def get_name(self) -> str:
        """Return the unique name for this recognizer."""
        return "pyaudio"

    def start_listening(self, callback: Callable[[str], None]) -> None:
        """
        Start listening for speech using PyAudio.

        Args:
            callback: Function to call with transcribed text.
        """
        if self._is_listening_state:
            self.logger.warning("Already listening, start_listening called again.")
            return

        self.logger.info("Starting PyAudio speech recognition.")
        self._is_listening_state = True
        self._stop_requested.clear()
        self._callback = callback
        
        self._listen_thread = threading.Thread(
            target=self._listen_loop,
            daemon=True
        )
        self._listen_thread.start()

    def _listen_loop(self) -> None:
        """
        Main listening loop that captures audio from the microphone using PyAudio.

        This loop runs in a separate thread. It continuously listens for audio input,
        adjusts for ambient noise once at the beginning, and then processes captured
        audio segments. Each segment is passed to the base class for recognition.
        The loop can be stopped via the `_stop_requested` event.
        """
        try:
            with sr.Microphone() as source:
                self.logger.info("Adjusting for ambient noise (PyAudio)...")
                try:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    self.logger.info("Ambient noise adjustment complete (PyAudio).")
                except Exception as e:
                    self.logger.error(f"Error during ambient noise adjustment: {e}. Continuing...")

                while not self._stop_requested.is_set():
                    if not self._is_listening_state: # Double check, in case stop_listening was called
                        break
                    try:
                        self.logger.debug("Listening for speech via PyAudio...")
                        # The listen() method will block until a phrase is detected or timeout.
                        # The phrase_time_limit is crucial here.
                        audio = self.recognizer.listen(
                            source,
                            timeout=1.0, # Timeout for listen() to check stop_requested periodically
                            phrase_time_limit=self.dictation_timeout
                        )
                        
                        self.logger.debug("Audio captured with PyAudio, passing to base for recognition.")
                        if self._callback:
                            # Delegate recognition to the base class method
                            self._recognize_audio_with_google(audio, self._callback)
                        else:
                            self.logger.warning("No callback set, recognized audio will not be processed.")
                            
                    except sr.WaitTimeoutError:
                        # This is expected if no speech is detected within the timeout.
                        self.logger.debug("No speech detected within timeout (PyAudio).")
                        continue # Continue listening
                    except Exception as e:
                        # Log other errors but continue the loop to maintain robustness
                        self.logger.error(f"Error in PyAudio listen loop: {e}", exc_info=True)
                        time.sleep(0.1) # Small delay to prevent rapid error looping

        except sr.RequestError as e:
             self.logger.error(f"Could not access PyAudio microphone. Is PyAudio installed and configured? Error: {e}")
        except Exception as e:
            # This handles errors like microphone not found, permissions issues etc.
            self.logger.error(f"Critical error initializing/using microphone with PyAudio: {e}", exc_info=True)
        finally:
            self._is_listening_state = False # Ensure state is updated
            self.logger.info("PyAudio listener loop stopped.")
            # self._callback = None # Optionally clear callback

    def stop_listening(self) -> None:
        """Stop listening for speech."""
        if not self._is_listening_state and not self._stop_requested.is_set():
            self.logger.warning("Not currently listening, stop_listening called.")
            # return # If already stopped, do nothing.

        self.logger.info("Stopping PyAudio speech recognition.")
        self._stop_requested.set()
        self._is_listening_state = False # Set state immediately

        if self._listen_thread and self._listen_thread.is_alive():
            self.logger.debug("Waiting for PyAudio listener thread to join...")
            self._listen_thread.join(timeout=2.0) # Wait for 2 seconds
            if self._listen_thread.is_alive():
                self.logger.warning("PyAudio listener thread did not exit cleanly after timeout.")
        
        self._listen_thread = None
        # self._callback = None # Clear callback when stopping
        self.logger.info("PyAudio speech recognition stopped.")

    # The is_listening property is inherited from BaseAudioRecognizer
    # and uses self._is_listening_state which is correctly managed here.

    # get_status is inherited from BaseAudioRecognizer and should provide
    # the necessary information like 'is_listening' and 'dictation_timeout'.
    # No need to override unless adding PyAudio-specific status.

# Example usage (for testing purposes, typically not part of the class file)
# if __name__ == '__main__':
#     logging.basicConfig(level=logging.DEBUG)
#     recognizer = PyAudioRecognizer()
#
#     def my_callback(text):
#         print(f"CALLBACK: {text}")
#
#     recognizer.start_listening(my_callback)
#     try:
#         while recognizer.is_listening:
#             time.sleep(0.1)
#     except KeyboardInterrupt:
#         print("Interrupted by user")
#     finally:
#         recognizer.stop_listening()
#         print("Program finished.")
