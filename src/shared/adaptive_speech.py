"""
Provides the AdaptiveSpeechRecognizer class.

This module defines a speech recognizer that can adaptively select and manage
different underlying speech recognition backends (e.g., PyAudio, SoundDevice,
cloud-based services) based on availability and preference.
"""

import logging
# import os # Not directly used in this file
from typing import Optional, Callable, List, Dict, Any

# Import the new recognizer classes and the AbstractSpeechRecognizer interface
from src.shared.pyaudio_recognizer import PyAudioRecognizer
from src.shared.sounddevice_recognizer import SoundDeviceRecognizer
from src.shared.cloud_speech import WebAPIRecognizer, WindowsSpeechRecognizer, KeyboardInputRecognizer
from src.shared.recognizer_interface import AbstractSpeechRecognizer # For type hinting

class AdaptiveSpeechRecognizer:
    """
    Intelligent speech recognizer that tries multiple backends in order of preference.
    It manages instances of recognizers that adhere to the AbstractSpeechRecognizer interface.
    """
    
    def __init__(self):
        self.logger = logging.getLogger('mumble.adaptive_speech')
        self.current_recognizer: Optional[AbstractSpeechRecognizer] = None # Updated type hint
        self.recognizer_name: Optional[str] = None # Name of the current recognizer type
        self.failed_recognizers: set[str] = set()
        
        # Order of preference for speech recognizers (using names returned by get_name())
        self.recognizer_preferences: List[str] = [
            'pyaudio',        # PyAudioRecognizer
            'sounddevice',    # SoundDeviceRecognizer
            'windows_speech', # WindowsSpeechRecognizer
            'web_api',        # WebAPIRecognizer
            'keyboard'        # KeyboardInputRecognizer (fallback)
        ]
        
        self._initialize_best_recognizer()
    
    def _initialize_best_recognizer(self):
        """Initialize the best available speech recognizer"""
        
        for recognizer_type in self.recognizer_preferences:
            if recognizer_type in self.failed_recognizers:
                continue
                
            try:
                recognizer = self._create_recognizer(recognizer_type)
                if recognizer:
                    self.current_recognizer = recognizer
                    self.recognizer_name = recognizer_type
                    self.logger.info(f"Using {recognizer_type} speech recognition")
                    return
                    
            except Exception as e:
                self.logger.warning(f"Failed to initialize {recognizer_type} recognizer: {e}")
                self.failed_recognizers.add(recognizer_type)
                continue
        
        # If we get here, no recognizer worked
        raise RuntimeError("No speech recognition backend available")
    
    def _create_recognizer(self, recognizer_type: str) -> Optional[AbstractSpeechRecognizer]:
        """
        Creates a specific type of recognizer instance based on its name.

        Args:
            recognizer_type: The name of the recognizer to create (e.g., 'pyaudio').

        Returns:
            An instance of a recognizer class adhering to AbstractSpeechRecognizer, or None if creation fails.
        """
        
        self.logger.debug(f"Attempting to create recognizer: {recognizer_type}")
        
        if recognizer_type == 'pyaudio':
            try:
                return PyAudioRecognizer()
            except ImportError:
                self.logger.info("PyAudio or its dependencies not available. PyAudioRecognizer cannot be used.")
                return None
            except Exception as e:
                self.logger.warning(f"Failed to initialize PyAudioRecognizer: {e}", exc_info=True)
                return None
                
        elif recognizer_type == 'sounddevice':
            try:
                return SoundDeviceRecognizer()
            except ImportError:
                self.logger.info("SoundDevice or its dependencies not available. SoundDeviceRecognizer cannot be used.")
                return None
            except Exception as e:
                self.logger.warning(f"Failed to initialize SoundDeviceRecognizer: {e}", exc_info=True)
                return None
                
        elif recognizer_type == 'windows_speech':
            try:
                # WindowsSpeechRecognizer itself checks sys.platform
                return WindowsSpeechRecognizer()
            except OSError: # Raised by WindowsSpeechRecognizer if not on Windows
                self.logger.info("Windows Speech Recognition is not available on this platform.")
                return None
            except ImportError: # Should not happen if cloud_speech.py is present, but good for robustness
                self.logger.info("WindowsSpeechRecognizer could not be imported (missing cloud_speech module or dependencies).")
                return None
            except Exception as e:
                self.logger.warning(f"Failed to initialize WindowsSpeechRecognizer: {e}", exc_info=True)
                return None
                
        elif recognizer_type == 'web_api':
            try:
                return WebAPIRecognizer()
            except ImportError: # Should not happen
                self.logger.info("WebAPIRecognizer could not be imported.")
                return None
            except Exception as e:
                self.logger.warning(f"Failed to initialize WebAPIRecognizer: {e}", exc_info=True)
                return None
                
        elif recognizer_type == 'keyboard':
            try:
                return KeyboardInputRecognizer()
            except ImportError: # Should not happen
                self.logger.info("KeyboardInputRecognizer could not be imported.")
                return None
            except Exception as e:
                self.logger.error(f"Failed to initialize KeyboardInputRecognizer (fallback): {e}", exc_info=True)
                return None
        
        return None
    
    def get_available_recognizers(self) -> List[str]:
        """
        Get list of available speech recognizers by attempting to create them.
        This can be resource-intensive if called frequently.
        """
        available = []
        original_failed_set = self.failed_recognizers.copy() # Preserve current failed set
        
        for recognizer_name_pref in self.recognizer_preferences:
            try:
                # Temporarily clear failed status for the check, as _create_recognizer might depend on it indirectly
                # or we just want to see if it *can* be created right now.
                # However, _create_recognizer doesn't use self.failed_recognizers.
                recognizer_instance = self._create_recognizer(recognizer_name_pref)
                if recognizer_instance:
                    # Check if it has a get_name method, otherwise use preference name
                    name_to_add = recognizer_name_pref
                    try:
                        name_to_add = recognizer_instance.get_name()
                    except Exception: # pylint: disable=broad-except
                        self.logger.warning(f"Recognizer for type '{recognizer_name_pref}' does not have get_name().")
                    
                    available.append(name_to_add)
                    # Clean up the test instance if necessary (some recognizers might open resources)
                    # For simplicity, we assume __init__ is lightweight or __del__ handles cleanup.
                    del recognizer_instance 
            except Exception: # pylint: disable=broad-except
                # If _create_recognizer itself raises an unhandled error
                self.logger.debug(f"Could not create/verify recognizer {recognizer_name_pref} for availability check.")
        
        self.failed_recognizers = original_failed_set # Restore original failed set
        return available
    
    def switch_recognizer(self, new_recognizer_type: str) -> bool:
        """
        Manually switch to a specific recognizer type.

        Args:
            new_recognizer_type: The name of the recognizer type to switch to.

        Returns:
            True if successfully switched, False otherwise.
        """
        
        if self.current_recognizer and self.current_recognizer.is_listening:
            self.logger.info(f"Stopping current recognizer ({self.recognizer_name}) before switching.")
            self.current_recognizer.stop_listening()
        
        self.logger.info(f"Attempting to switch to recognizer: {new_recognizer_type}")
        try:
            new_recognizer_instance = self._create_recognizer(new_recognizer_type)
            if new_recognizer_instance:
                self.current_recognizer = new_recognizer_instance
                # Use the name from the instance itself, which should match new_recognizer_type
                self.recognizer_name = self.current_recognizer.get_name() 
                self.logger.info(f"Successfully switched to {self.recognizer_name} speech recognition.")
                # Remove from failed set if it was there
                if self.recognizer_name in self.failed_recognizers:
                    self.failed_recognizers.remove(self.recognizer_name)
                return True
            else:
                self.logger.error(f"Failed to create {new_recognizer_type} recognizer during switch.")
                self.failed_recognizers.add(new_recognizer_type) # Mark as failed
                # Attempt to re-initialize best available if current is now None
                if not self.current_recognizer:
                    self.logger.warning("No recognizer active after failed switch. Re-initializing.")
                    self._initialize_best_recognizer()
                return False
                
        except Exception as e:
            self.logger.error(f"Error switching to {new_recognizer_type}: {e}", exc_info=True)
            self.failed_recognizers.add(new_recognizer_type)
            if not self.current_recognizer: # If current recognizer became invalid
                self.logger.warning("Current recognizer is invalid after error. Re-initializing.")
                self._initialize_best_recognizer()
            return False
    
    @property
    def is_listening(self) -> bool:
        """Return whether the current recognizer is currently listening."""
        if self.current_recognizer:
            try:
                return self.current_recognizer.is_listening
            except Exception as e:
                self.logger.error(f"Error getting is_listening status from {self.recognizer_name}: {e}", exc_info=True)
                # Handle potential errors from the recognizer instance (e.g., if it became corrupted)
                self._handle_recognizer_error()
                return False # Assume not listening if an error occurs
        return False
    
    def start_listening(self, callback: Callable[[str], None]) -> None:
        """
        Start listening for speech using the current active recognizer.
        If the current recognizer fails, it attempts to switch to the next available one.
        """
        if not self.current_recognizer:
            self.logger.error("No speech recognizer available to start listening.")
            # Attempt to initialize one if none is set (e.g., if all failed on startup)
            self._initialize_best_recognizer()
            if not self.current_recognizer:
                 raise RuntimeError("No speech recognizer could be initialized.")
        
        # Add error handling wrapper to callback to prevent user callback errors from crashing the listener
        def wrapped_callback(text: str):
            try:
                callback(text)
            except Exception as e:
                self.logger.error(f"Error in user-provided speech callback: {e}", exc_info=True)
        
        try:
            self.logger.info(f"Starting listening with {self.recognizer_name} recognizer.")
            self.current_recognizer.start_listening(wrapped_callback)
        except Exception as e:
            self.logger.error(f"Error starting {self.recognizer_name} recognizer: {e}", exc_info=True)
            self._handle_recognizer_error(attempt_restart_listening=True, callback=wrapped_callback)

    def _handle_recognizer_error(self, attempt_restart_listening: bool = False, callback: Optional[Callable[[str], None]] = None):
        """Handles errors from the current recognizer and tries to fall back."""
        if self.recognizer_name: # Ensure there was a recognizer name to mark as failed
            self.failed_recognizers.add(self.recognizer_name)
        
        self.logger.warning(f"Recognizer {self.recognizer_name or 'unknown'} failed. Attempting to find a fallback.")
        self.current_recognizer = None # Clear the failed recognizer
        self.recognizer_name = None

        self._initialize_best_recognizer() # This will try to find the next best recognizer

        if self.current_recognizer:
            self.logger.info(f"Successfully fell back to {self.recognizer_name} recognizer.")
            if attempt_restart_listening and callback:
                try:
                    self.logger.info(f"Attempting to restart listening with new recognizer: {self.recognizer_name}")
                    self.current_recognizer.start_listening(callback)
                except Exception as ex_inner:
                    self.logger.error(f"Failed to restart listening with fallback {self.recognizer_name}: {ex_inner}", exc_info=True)
                    # Potentially trigger another round of error handling, or give up.
                    # For now, we give up to avoid infinite loops.
                    raise RuntimeError(f"All speech recognizers, including fallback {self.recognizer_name}, have failed during restart.") from ex_inner
            elif attempt_restart_listening:
                 self.logger.error("Cannot restart listening: callback not provided to _handle_recognizer_error.")

        else:
            self.logger.error("All speech recognizers have failed. No fallback available.")
            if attempt_restart_listening: # Only raise if we were trying to restart
                raise RuntimeError("All speech recognizers have failed. Cannot start listening.")

    def stop_listening(self) -> None:
        """Stop listening for speech on the current recognizer."""
        if self.current_recognizer:
            try:
                self.logger.info(f"Stopping listening with {self.recognizer_name} recognizer.")
                self.current_recognizer.stop_listening()
            except Exception as e:
                self.logger.error(f"Error stopping {self.recognizer_name} recognizer: {e}", exc_info=True)
                # Even if stop fails, we should probably try to clean up state.
                # This might involve more aggressive cleanup or just logging.
                # For now, we assume stop_listening in concrete classes is robust or this is a critical failure.
                self._handle_recognizer_error() # Try to recover or mark as failed
        else:
            self.logger.info("No active recognizer to stop.")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status information about the adaptive recognizer and its active backend."""
        status = {
            'adaptive_recognizer_status': 'active' if self.current_recognizer else 'inactive',
            'current_recognizer_name': self.recognizer_name if self.current_recognizer else None,
            'is_listening': self.is_listening, # Uses the property, which has error handling
            'available_recognizer_preferences': self.recognizer_preferences,
            'failed_recognizers_session': list(self.failed_recognizers)
        }
        if self.current_recognizer:
            try:
                status['current_recognizer_details'] = self.current_recognizer.get_status()
            except Exception as e:
                self.logger.warning(f"Could not get status from {self.recognizer_name}: {e}")
                status['current_recognizer_details'] = {"error": "Failed to retrieve status"}
        else:
            status['current_recognizer_details'] = None
            
        return status

# Convenience function for easy import, remains unchanged.
def create_adaptive_speech_recognizer():
    """Create an adaptive speech recognizer"""
    return AdaptiveSpeechRecognizer() 