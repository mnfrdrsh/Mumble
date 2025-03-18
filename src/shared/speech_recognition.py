"""
Shared speech recognition module for Mumble applications
"""

import os
import speech_recognition as sr
import logging
import threading
import time
import traceback
from typing import Optional, Callable

class SpeechRecognizer:
    """Core speech recognition functionality shared between Mumble applications"""
    
    def __init__(self):
        """Initialize the speech recognizer"""
        self.recognizer = sr.Recognizer()
        self.logger = logging.getLogger('mumble.speech')
        self._is_listening = False
        self._stop_requested = False
        self._listen_thread = None
        
        # Get timeout from environment variable or use default
        try:
            self.dictation_timeout = int(os.environ.get("MUMBLE_DICTATION_TIMEOUT", "5"))
        except (ValueError, TypeError):
            self.dictation_timeout = 5  # Default timeout in seconds
            
        self.logger.info(f"Dictation timeout set to {self.dictation_timeout} seconds")
        
    @property
    def is_listening(self) -> bool:
        """Return whether the recognizer is currently listening"""
        return self._is_listening
        
    def start_listening(self, callback: Callable[[str], None]) -> None:
        """
        Start listening for speech
        
        Args:
            callback: Function to call with transcribed text
        """
        if self._is_listening:
            return
            
        self._is_listening = True
        self._stop_requested = False
        self.logger.info("Starting speech recognition")
        
        # Start listening in a separate thread
        self._listen_thread = threading.Thread(
            target=self._listen_loop,
            args=(callback,),
            daemon=True
        )
        self._listen_thread.start()
            
    def _listen_loop(self, callback: Callable[[str], None]) -> None:
        """
        Main listening loop that runs in a separate thread
        
        Args:
            callback: Function to call with transcribed text
        """
        try:
            with sr.Microphone() as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                self.logger.info("Adjusted for ambient noise")
                
                while self._is_listening and not self._stop_requested:
                    try:
                        self.logger.debug("Waiting for speech...")
                        
                        # Use a timeout to prevent hanging
                        audio = self.recognizer.listen(
                            source, 
                            timeout=2.0,  # Short timeout to allow checking stop flag
                            phrase_time_limit=self.dictation_timeout
                        )
                        
                        self.logger.debug("Audio captured, recognizing...")
                        
                        # Use a thread with timeout for recognition to prevent hanging
                        recognition_result = [None]
                        recognition_error = [None]
                        
                        def recognize_worker():
                            try:
                                recognition_result[0] = self.recognizer.recognize_google(audio)
                            except sr.UnknownValueError:
                                self.logger.debug("Speech was unintelligible")
                            except sr.RequestError as e:
                                self.logger.error(f"Could not request results: {e}")
                                recognition_error[0] = e
                            except Exception as e:
                                self.logger.error(f"Error during speech recognition: {e}")
                                self.logger.error(traceback.format_exc())
                                recognition_error[0] = e
                        
                        # Start recognition in a thread
                        recognition_thread = threading.Thread(target=recognize_worker)
                        recognition_thread.daemon = True
                        recognition_thread.start()
                        
                        # Wait for recognition with timeout
                        recognition_thread.join(timeout=10.0)  # 10 second timeout for API call
                        
                        if recognition_thread.is_alive():
                            self.logger.error("Recognition timed out, skipping this audio")
                            continue
                            
                        if recognition_error[0]:
                            self.logger.error(f"Recognition error: {recognition_error[0]}")
                            # Don't break the loop for transient errors
                            time.sleep(0.5)  # Small delay before retrying
                            continue
                            
                        text = recognition_result[0]
                        if text and callback:
                            self.logger.info(f"Recognized: {text}")
                            callback(text)
                            
                    except sr.WaitTimeoutError:
                        # This is normal when no speech is detected
                        pass
                    except Exception as e:
                        self.logger.error(f"Unexpected error in listen loop: {e}")
                        self.logger.error(traceback.format_exc())
                        time.sleep(0.5)  # Small delay before retrying
                        
        except Exception as e:
            self.logger.error(f"Error initializing microphone: {e}")
            self.logger.error(traceback.format_exc())
        finally:
            self._is_listening = False
            self.logger.info("Listening thread stopped")
            
    def stop_listening(self) -> None:
        """Stop listening for speech"""
        if not self._is_listening:
            return
            
        self.logger.info("Stopping speech recognition")
        self._stop_requested = True
        self._is_listening = False
        
        # Wait for the thread to finish, but with a timeout
        if self._listen_thread and self._listen_thread.is_alive():
            self._listen_thread.join(timeout=2.0)
            if self._listen_thread.is_alive():
                self.logger.warning("Listening thread did not exit cleanly") 