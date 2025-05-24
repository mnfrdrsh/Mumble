"""
Adaptive speech recognition that automatically selects the best available backend
"""

import logging
import os
from typing import Optional, Callable, List, Dict, Any

class AdaptiveSpeechRecognizer:
    """
    Intelligent speech recognizer that tries multiple backends in order of preference
    """
    
    def __init__(self):
        self.logger = logging.getLogger('mumble.adaptive_speech')
        self.current_recognizer = None
        self.recognizer_name = None
        self.failed_recognizers = set()
        
        # Order of preference for speech recognizers
        self.recognizer_preferences = [
            'original',      # PyAudio-based (if available)
            'sounddevice',   # sounddevice-based alternative
            'windows',       # Windows Speech Recognition
            'web',           # Web Speech API
            'keyboard'       # Keyboard fallback
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
    
    def _create_recognizer(self, recognizer_type: str):
        """Create a specific type of recognizer"""
        
        if recognizer_type == 'original':
            try:
                from .speech_recognition import SpeechRecognizer
                return SpeechRecognizer()
            except ImportError as e:
                if 'pyaudio' in str(e).lower():
                    self.logger.info("PyAudio not available, trying alternatives...")
                    return None
                raise
                
        elif recognizer_type == 'sounddevice':
            try:
                from .speech_recognition_alt import SpeechRecognizerAlt
                return SpeechRecognizerAlt()
            except ImportError as e:
                self.logger.info(f"sounddevice not available: {e}")
                return None
                
        elif recognizer_type == 'windows':
            try:
                import sys
                if sys.platform == 'win32':
                    from .cloud_speech import WindowsSpeechRecognizer
                    return WindowsSpeechRecognizer()
                else:
                    return None
            except Exception as e:
                self.logger.info(f"Windows speech not available: {e}")
                return None
                
        elif recognizer_type == 'web':
            try:
                from .cloud_speech import WebAPIRecognizer
                return WebAPIRecognizer()
            except Exception as e:
                self.logger.info(f"Web speech not available: {e}")
                return None
                
        elif recognizer_type == 'keyboard':
            try:
                from .cloud_speech import KeyboardInputRecognizer
                return KeyboardInputRecognizer()
            except Exception as e:
                self.logger.error(f"Even keyboard fallback failed: {e}")
                return None
        
        return None
    
    def get_available_recognizers(self) -> List[str]:
        """Get list of available speech recognizers"""
        available = []
        
        for recognizer_type in self.recognizer_preferences:
            try:
                recognizer = self._create_recognizer(recognizer_type)
                if recognizer:
                    available.append(recognizer_type)
            except:
                pass
                
        return available
    
    def switch_recognizer(self, recognizer_type: str) -> bool:
        """Manually switch to a specific recognizer type"""
        
        if self.current_recognizer and self.current_recognizer.is_listening:
            self.current_recognizer.stop_listening()
        
        try:
            new_recognizer = self._create_recognizer(recognizer_type)
            if new_recognizer:
                self.current_recognizer = new_recognizer
                self.recognizer_name = recognizer_type
                self.logger.info(f"Switched to {recognizer_type} speech recognition")
                return True
            else:
                self.logger.error(f"Failed to create {recognizer_type} recognizer")
                return False
                
        except Exception as e:
            self.logger.error(f"Error switching to {recognizer_type}: {e}")
            return False
    
    @property
    def is_listening(self) -> bool:
        """Return whether the recognizer is currently listening"""
        if self.current_recognizer:
            return self.current_recognizer.is_listening
        return False
    
    def start_listening(self, callback: Callable[[str], None]) -> None:
        """Start listening for speech"""
        if not self.current_recognizer:
            raise RuntimeError("No speech recognizer available")
        
        # Add error handling wrapper to callback
        def wrapped_callback(text: str):
            try:
                callback(text)
            except Exception as e:
                self.logger.error(f"Error in speech callback: {e}")
        
        try:
            self.current_recognizer.start_listening(wrapped_callback)
        except Exception as e:
            self.logger.error(f"Error starting {self.recognizer_name} recognizer: {e}")
            
            # Try to fall back to next available recognizer
            self.failed_recognizers.add(self.recognizer_name)
            remaining_recognizers = [r for r in self.recognizer_preferences 
                                   if r not in self.failed_recognizers]
            
            if remaining_recognizers:
                self.logger.info(f"Trying fallback recognizer: {remaining_recognizers[0]}")
                self._initialize_best_recognizer()
                if self.current_recognizer:
                    self.current_recognizer.start_listening(wrapped_callback)
            else:
                raise RuntimeError("All speech recognizers have failed")
    
    def stop_listening(self) -> None:
        """Stop listening for speech"""
        if self.current_recognizer:
            self.current_recognizer.stop_listening()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status information"""
        return {
            'current_recognizer': self.recognizer_name,
            'is_listening': self.is_listening,
            'available_recognizers': self.get_available_recognizers(),
            'failed_recognizers': list(self.failed_recognizers)
        }

# Convenience function for easy import
def create_adaptive_speech_recognizer():
    """Create an adaptive speech recognizer"""
    return AdaptiveSpeechRecognizer() 