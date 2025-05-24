"""
Alternative speech recognition module using sounddevice instead of PyAudio
Provides the same interface as the original speech_recognition.py
"""

import os
import logging
import threading
import time
import traceback
import tempfile
import wave
from typing import Optional, Callable

try:
    import sounddevice as sd
    import soundfile as sf
    import numpy as np
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

class SpeechRecognizerAlt:
    """Alternative speech recognition using sounddevice instead of PyAudio"""
    
    def __init__(self):
        """Initialize the speech recognizer"""
        self.logger = logging.getLogger('mumble.speech_alt')
        
        if not SOUNDDEVICE_AVAILABLE:
            raise ImportError("sounddevice is required but not installed. Run: pip install sounddevice soundfile")
            
        if not SPEECH_RECOGNITION_AVAILABLE:
            raise ImportError("SpeechRecognition is required but not installed. Run: pip install SpeechRecognition")
        
        self.recognizer = sr.Recognizer()
        self._is_listening = False
        self._stop_requested = False
        self._listen_thread = None
        
        # Audio settings
        self.sample_rate = 16000
        self.channels = 1
        self.chunk_duration = 1.0  # seconds
        
        # Get timeout from environment variable or use default
        try:
            self.dictation_timeout = int(os.environ.get("MUMBLE_DICTATION_TIMEOUT", "5"))
        except (ValueError, TypeError):
            self.dictation_timeout = 5
            
        self.logger.info(f"Alternative speech recognizer initialized with timeout {self.dictation_timeout}s")
        
        # Test audio devices
        try:
            devices = sd.query_devices()
            input_devices = [d for d in devices if d['max_input_channels'] > 0]
            if not input_devices:
                self.logger.warning("No input audio devices found")
            else:
                default_input = sd.query_devices(kind='input')
                self.logger.info(f"Using audio device: {default_input['name']}")
        except Exception as e:
            self.logger.error(f"Error querying audio devices: {e}")
    
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
        self.logger.info("Starting speech recognition with sounddevice")
        
        # Start listening in a separate thread
        self._listen_thread = threading.Thread(
            target=self._listen_loop,
            args=(callback,),
            daemon=True
        )
        self._listen_thread.start()
        
    def _listen_loop(self, callback: Callable[[str], None]) -> None:
        """
        Main listening loop using sounddevice
        
        Args:
            callback: Function to call with transcribed text
        """
        try:
            # Calculate chunk size
            chunk_size = int(self.sample_rate * self.chunk_duration)
            
            while self._is_listening and not self._stop_requested:
                try:
                    self.logger.debug("Recording audio...")
                    
                    # Record audio chunk
                    audio_data = sd.rec(
                        chunk_size, 
                        samplerate=self.sample_rate, 
                        channels=self.channels,
                        dtype=np.int16
                    )
                    sd.wait()  # Wait for recording to complete
                    
                    if self._stop_requested:
                        break
                        
                    # Check for silence (simple energy-based detection)
                    energy = np.sum(audio_data.astype(np.float32) ** 2)
                    if energy < 1000:  # Adjust threshold as needed
                        continue
                        
                    self.logger.debug("Audio captured, recognizing...")
                    
                    # Save to temporary WAV file for SpeechRecognition
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                        temp_path = temp_file.name
                        
                    # Write audio data to WAV file
                    sf.write(temp_path, audio_data, self.sample_rate)
                    
                    try:
                        # Use speech_recognition with the audio file
                        with sr.AudioFile(temp_path) as source:
                            audio = self.recognizer.record(source)
                            
                        # Recognize speech with timeout
                        text = self._recognize_with_timeout(audio)
                        
                        if text and callback:
                            self.logger.info(f"Recognized: {text}")
                            callback(text)
                            
                    finally:
                        # Clean up temporary file
                        try:
                            os.unlink(temp_path)
                        except:
                            pass
                            
                except Exception as e:
                    self.logger.error(f"Error in listen loop: {e}")
                    self.logger.error(traceback.format_exc())
                    time.sleep(0.5)
                    
        except Exception as e:
            self.logger.error(f"Error initializing audio recording: {e}")
            self.logger.error(traceback.format_exc())
        finally:
            self._is_listening = False
            self.logger.info("Listening thread stopped")
    
    def _recognize_with_timeout(self, audio) -> Optional[str]:
        """Recognize speech with timeout protection"""
        result = [None]
        error = [None]
        
        def recognize_worker():
            try:
                result[0] = self.recognizer.recognize_google(audio)
            except sr.UnknownValueError:
                self.logger.debug("Speech was unintelligible")
            except sr.RequestError as e:
                self.logger.error(f"Could not request results: {e}")
                error[0] = e
            except Exception as e:
                self.logger.error(f"Error during speech recognition: {e}")
                error[0] = e
        
        # Start recognition in a thread
        recognition_thread = threading.Thread(target=recognize_worker)
        recognition_thread.daemon = True
        recognition_thread.start()
        
        # Wait for recognition with timeout
        recognition_thread.join(timeout=10.0)
        
        if recognition_thread.is_alive():
            self.logger.error("Recognition timed out")
            return None
            
        if error[0]:
            self.logger.error(f"Recognition error: {error[0]}")
            return None
            
        return result[0]
    
    def stop_listening(self) -> None:
        """Stop listening for speech"""
        if not self._is_listening:
            return
            
        self.logger.info("Stopping speech recognition")
        self._stop_requested = True
        self._is_listening = False
        
        # Wait for thread to finish
        if self._listen_thread and self._listen_thread.is_alive():
            self._listen_thread.join(timeout=2.0)
            if self._listen_thread.is_alive():
                self.logger.warning("Listening thread did not exit cleanly")

class WebSpeechAPI:
    """Web-based speech recognition using browser APIs (requires web interface)"""
    
    def __init__(self):
        self.logger = logging.getLogger('mumble.web_speech')
        self._is_listening = False
        
    def is_supported(self) -> bool:
        """Check if web speech API is supported"""
        # This would require a web browser integration
        return False
    
    def start_listening(self, callback):
        """Start web-based speech recognition"""
        self.logger.info("Web Speech API not implemented yet")
        
    def stop_listening(self):
        """Stop web-based speech recognition"""
        pass

# Factory function to create the best available recognizer
def create_speech_recognizer():
    """Create the best available speech recognizer"""
    if SOUNDDEVICE_AVAILABLE and SPEECH_RECOGNITION_AVAILABLE:
        return SpeechRecognizerAlt()
    else:
        # Fallback to original if available
        try:
            from .speech_recognition import SpeechRecognizer
            return SpeechRecognizer()
        except ImportError:
            raise ImportError("No speech recognition backend available. Install either PyAudio or sounddevice.") 