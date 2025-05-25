"""
SoundDevice-based speech recognizer for Mumble applications.
"""

import logging
import threading
# import time # Not directly used
import tempfile
import os # Keep for os.unlink if tempfile.NamedTemporaryFile(delete=False) is used
from typing import Optional, Callable, Any # Added Any for np dummy

try:
    import sounddevice as sd
    import soundfile as sf
    import numpy as np
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False
    # Define dummy types if not available for type hinting purposes in the class
    class np: # type: ignore # pylint: disable=invalid-name
        """Dummy numpy for type hinting when numpy is not installed."""
        ndarray: Any = type(None) 
        int16: Any = type(None) 
        float32: Any = type(None) 
        @staticmethod
        def sum(*args: Any, **kwargs: Any) -> float: # type: ignore
            """Dummy sum method."""
            return 0.0

# speech_recognition is also a dependency for BaseAudioRecognizer
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True # Should be true if BaseAudioRecognizer can be imported
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False


from src.shared.base_audio_recognizer import BaseAudioRecognizer

class SoundDeviceRecognizer(BaseAudioRecognizer):
    """
    Speech recognizer implementation using SoundDevice for audio input.

    This class handles capturing audio from the microphone via SoundDevice,
    processes it, and uses the base class to perform speech recognition.
    """

    def __init__(self):
        """Initialize the SoundDeviceRecognizer."""
        if not SOUNDDEVICE_AVAILABLE:
            raise ImportError(
                "SoundDevice and/or SoundFile are not installed. "
                "Please install them: pip install sounddevice soundfile numpy"
            )
        if not SPEECH_RECOGNITION_AVAILABLE: # Should be caught by BaseAudioRecognizer already
            raise ImportError(
                "SpeechRecognition library is not installed. "
                "Please install it: pip install SpeechRecognition"
            )

        super().__init__(logger_name='mumble.sounddevice_speech')
        
        self._stop_requested = threading.Event()
        self._listen_thread: Optional[threading.Thread] = None
        self._callback: Optional[Callable[[str], None]] = None

        # Audio settings specific to sounddevice capture
        self.sample_rate: int = 16000  # Standard sample rate for speech
        self.channels: int = 1         # Mono audio
        # self.chunk_duration_seconds: float = 1.0 # How much audio to record at a time
        # The dictation_timeout from base class will be used as phrase_time_limit

        # Log available input devices
        try:
            devices = sd.query_devices()
            input_devices = [d for d in devices if d['max_input_channels'] > 0] # type: ignore
            if not input_devices:
                self.logger.warning("No input audio devices found by sounddevice.")
            else:
                default_input = sd.query_devices(kind='input') # type: ignore
                self.logger.info(f"SoundDevice using audio input device: {default_input['name']}") # type: ignore
        except Exception as e:
            self.logger.error(f"SoundDevice error querying audio devices: {e}")


    def get_name(self) -> str:
        """Return the unique name for this recognizer."""
        return "sounddevice"

    def start_listening(self, callback: Callable[[str], None]) -> None:
        """
        Start listening for speech using SoundDevice.

        Args:
            callback: Function to call with transcribed text.
        """
        if not SOUNDDEVICE_AVAILABLE:
            self.logger.error("SoundDevice is not available. Cannot start listening.")
            return

        if self._is_listening_state:
            self.logger.warning("Already listening (SoundDevice), start_listening called again.")
            return

        self.logger.info("Starting SoundDevice speech recognition.")
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
        Main listening loop using SoundDevice for audio capture.

        This loop runs in a separate thread. It records audio segments of
        `self.dictation_timeout` duration. Each segment is checked for silence;
        if not silent, it's saved as a temporary WAV file, then converted to
        `AudioData` and passed to the base class for recognition.
        The loop can be stopped via `_stop_requested`. It also handles
        `PortAudioError` gracefully by stopping the listener.
        """
        # Calculate frame count for recording based on dictation_timeout
        # This means each recording will be at most dictation_timeout seconds long.
        frames_to_record = int(self.sample_rate * self.dictation_timeout)

        try:
            while not self._stop_requested.is_set():
                if not self._is_listening_state: # Check if listening state was changed externally
                    break
                
                temp_audio_path: Optional[str] = None
                try:
                    self.logger.debug(
                        f"Recording audio with SoundDevice for up to {self.dictation_timeout}s..."
                    )
                    
                    # Record audio data using sounddevice; sd.rec() returns a NumPy array
                    audio_segment_np: np.ndarray = sd.rec( # type: ignore
                        frames=frames_to_record,
                        samplerate=self.sample_rate,
                        channels=self.channels,
                        dtype=np.int16 # type: ignore # Common format for WAV files
                    )
                    sd.wait()  # Wait for the recording to complete

                    if self._stop_requested.is_set(): # Check immediately after blocking call
                        break

                    # Simple silence detection (can be tuned or made more sophisticated)
                    # Energy threshold might need adjustment based on microphone sensitivity and environment.
                    energy = np.sum(audio_segment_np.astype(np.float32) ** 2) # type: ignore
                    # self.logger.debug(f"Audio segment energy: {energy}") # For tuning threshold
                    silence_threshold = 10000 # Arbitrary threshold, may need tuning
                    if energy < silence_threshold:
                        self.logger.debug(
                            f"SoundDevice detected silence or low audio energy ({energy} < {silence_threshold}), skipping."
                        )
                        continue # Skip processing this segment
                    
                    self.logger.debug("Audio captured with SoundDevice, preparing for recognition.")

                    # Convert numpy array to speech_recognition.AudioData
                    # This typically requires saving to a WAV file first, then loading with sr.AudioFile
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_wav_file:
                        temp_audio_path = tmp_wav_file.name
                    
                    sf.write(temp_audio_path, audio_segment_np, self.sample_rate) # type: ignore

                    with sr.AudioFile(temp_audio_path) as source: # Load audio from file
                        audio_data_sr = self.recognizer.record(source) # Convert to AudioData

                    if self._callback:
                        # Delegate recognition to the base class method
                        self._recognize_audio_with_google(audio_data_sr, self._callback)
                    else:
                        self.logger.warning(
                            "No callback set (SoundDevice), recognized audio will not be processed."
                        )

                except sd.PortAudioError as pae: # type: ignore
                    self.logger.error(
                        f"SoundDevice PortAudioError in listen loop: {pae}. "
                        "This might indicate issues with the audio device or drivers. Stopping listener.", 
                        exc_info=True
                    )
                    # Stop listening to prevent rapid error loops if the device is truly problematic.
                    self._is_listening_state = False
                    self._stop_requested.set() # Ensure the main while loop also exits
                    break # Exit the inner try-except-finally and then the while loop
                except Exception as e:
                    self.logger.error(f"Error in SoundDevice listen loop's try block: {e}", exc_info=True)
                    # Consider a short sleep to prevent rapid looping on persistent errors not caught above
                    try:
                        # Check if stop was requested during the error handling itself.
                        if self._stop_requested.wait(timeout=0.1): # Non-blocking check
                           break 
                    except Exception: # pylint: disable=broad-except
                        pass # Ignore errors from wait itself
                finally:
                    # Clean up the temporary WAV file if it was created
                    if temp_audio_path and os.path.exists(temp_audio_path):
                        try:
                            os.unlink(temp_audio_path)
                        except OSError as e_unlink:
                            self.logger.error(f"Error deleting temporary WAV file {temp_audio_path}: {e_unlink}")
            
        except Exception as e: # Catch errors from the main while loop setup (e.g., if sd module itself has issues)
            # This might catch errors during sd.Stream() setup if that was used,
            # or other unexpected issues.
            self.logger.error(
                f"Critical error in SoundDevice listener setup or unhandled loop exception: {e}",
                exc_info=True
            )
        finally:
            self._is_listening_state = False # Ensure state is updated
            self.logger.info("SoundDevice listener loop stopped.")


    def stop_listening(self) -> None:
        """Stop listening for speech."""
        if not self._is_listening_state and not self._stop_requested.is_set():
            self.logger.warning("Not currently listening (SoundDevice), stop_listening called.")
            # return

        self.logger.info("Stopping SoundDevice speech recognition.")
        self._stop_requested.set() # Signal the loop to stop
        # sd.stop() # If using InputStream, this would be needed. For sd.rec, wait() should handle it.
        
        self._is_listening_state = False # Set state immediately

        if self._listen_thread and self._listen_thread.is_alive():
            self.logger.debug("Waiting for SoundDevice listener thread to join...")
            self._listen_thread.join(timeout=2.0) 
            if self._listen_thread.is_alive():
                self.logger.warning("SoundDevice listener thread did not exit cleanly after timeout.")
        
        self._listen_thread = None
        self.logger.info("SoundDevice speech recognition stopped.")

    # is_listening property is inherited from BaseAudioRecognizer.
    # get_status is inherited from BaseAudioRecognizer.
    # _recognize_audio_with_google is inherited from BaseAudioRecognizer.
    
    # Removed _recognize_with_timeout as it's handled by base class.
    # Removed create_speech_recognizer factory.
    # Removed WebSpeechAPI class.

# Example usage (for testing purposes, typically not part of the class file)
# if __name__ == '__main__':
#     if not SOUNDDEVICE_AVAILABLE:
#         print("SoundDevice or its dependencies not available. Skipping example.")
#     else:
#         logging.basicConfig(level=logging.DEBUG)
#         recognizer = SoundDeviceRecognizer()
#
#         def my_callback(text):
#             print(f"SOUNDDEVICE CALLBACK: {text}")
#
#         try:
#             recognizer.start_listening(my_callback)
#             while recognizer.is_listening:
#                 time.sleep(0.1)
#         except ImportError as e:
#             print(f"Could not run example: {e}")
#         except KeyboardInterrupt:
#             print("Interrupted by user (SoundDevice)")
#         finally:
#             if 'recognizer' in locals() and recognizer.is_listening:
#                 recognizer.stop_listening()
#             print("Program finished (SoundDevice).")
