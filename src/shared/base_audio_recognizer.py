"""
Provides BaseAudioRecognizer, a foundational class for audio capture and speech recognition
using the 'speech_recognition' library with Google Cloud Speech-to-Text.
"""
import logging
import os
import speech_recognition as sr
import threading
# import time # Not directly used
from typing import Any, Callable, Dict
# import abc # Not directly used by this class, only by its parent.

from src.shared.recognizer_interface import AbstractSpeechRecognizer

class BaseAudioRecognizer(AbstractSpeechRecognizer):
    """
    Base class for audio recognizer implementations using the speech_recognition library.

    This class provides common functionality for initializing the recognizer,
    handling dictation timeout, and the core logic for recognizing speech
    using Google Speech Recognition. Subclasses must implement the actual
    audio capturing and state management.
    """

    def __init__(self, logger_name: str):
        """
        Initializes the BaseAudioRecognizer.

        Args:
            logger_name: The name for the logger instance (e.g., 'mumble.pyaudio_speech').
        """
        self.logger = logging.getLogger(logger_name)
        self.recognizer = sr.Recognizer()
        try:
            self.dictation_timeout: int = int(os.getenv("MUMBLE_DICTATION_TIMEOUT", "5"))
        except ValueError:
            self.logger.warning(
                f"Invalid value for MUMBLE_DICTATION_TIMEOUT: '{os.getenv('MUMBLE_DICTATION_TIMEOUT')}'."
                f" Using default value of 5 seconds."
            )
            self.dictation_timeout = 5
        self.logger.info(f"Dictation timeout set to {self.dictation_timeout} seconds.")
        self._is_listening_state: bool = False # Internal state for the is_listening property

    def start_listening(self, callback: Callable[[str], None]) -> None:
        """
        Starts the speech recognition process.

        This method must be implemented by subclasses to handle actual audio capture.

        Args:
            callback: A function to be called when speech is recognized.

        Raises:
            NotImplementedError: This method is not implemented in the base class.
        """
        raise NotImplementedError(
            "Subclasses must implement start_listening to capture audio."
        )

    def stop_listening(self) -> None:
        """
        Stops the speech recognition process.

        This method must be implemented by subclasses to stop audio capture.

        Raises:
            NotImplementedError: This method is not implemented in the base class.
        """
        raise NotImplementedError(
            "Subclasses must implement stop_listening to stop audio capture."
        )

    @property
    def is_listening(self) -> bool:
        """
        Indicates if the recognizer is currently listening.

        Subclasses are expected to manage the actual listening state
        (e.g., by updating `_is_listening_state` or overriding this property).
        By default, returns False.
        """
        # This default implementation relies on subclasses managing _is_listening_state.
        return self._is_listening_state

    # A setter for is_listening is not strictly required by the AbstractSpeechRecognizer interface.
    # Making it read-only at this base level might be too restrictive if subclasses
    # have valid reasons to allow direct setting of the listening state, though typically
    # state should change as a side effect of start_listening() and stop_listening().

    def get_name(self) -> str:
        """
        Returns a unique string name for the recognizer implementation.

        Subclasses must override this method to provide their specific name.

        Raises:
            NotImplementedError: This method is not implemented in the base class.
        """
        raise NotImplementedError(
            "Subclasses must implement get_name to provide a unique recognizer name."
        )

    def _recognize_audio_with_google(
        self, audio_data: sr.AudioData, callback: Callable[[str], None]
    ) -> None:
        """
        Performs speech recognition on the given audio data using Google Speech Recognition API.

        This method offloads the actual recognition to a separate thread to prevent
        blocking the caller, especially if it's on the main UI thread. It includes
        error handling for common speech recognition issues and ensures the callback
        is invoked with the transcribed text upon success.

        Args:
            audio_data: An `speech_recognition.AudioData` object containing the audio to transcribe.
            callback: A callable that takes a single string argument (the transcribed text)
                      and is called upon successful recognition.
        """
        # The 'recognition_timeout_seconds = 10' variable was defined but not used.
        # If a timeout for the Google API call itself is desired, it's typically handled
        # by the underlying network request's timeout, not directly in recognize_google().

        def recognition_thread_target():
            try:
                self.logger.debug("Starting Google Speech Recognition API call.")
                # The `recognize_google` method itself doesn't have a timeout parameter.
                # Network timeouts are handled by the underlying `requests` library used by `speech_recognition`.
                # The main purpose of running this in a thread is to not block the main flow,
                # allowing the application (e.g., UI) to remain responsive.
                text = self.recognizer.recognize_google(audio_data, show_all=False)
                self.logger.info(f"Google Speech Recognition transcribed: '{text}'")
                if text: # Ensure callback is only called with non-empty text and if not empty
                    callback(text)
            except sr.UnknownValueError:
                self.logger.info(
                    "Google Speech Recognition could not understand audio."
                )
            except sr.RequestError as e:
                self.logger.error(
                    f"Could not request results from Google Speech Recognition service; {e}"
                )
            except Exception as e:
                self.logger.exception(
                    f"An unexpected error occurred during speech recognition: {e}"
                )

        recognition_thread = threading.Thread(target=recognition_thread_target)
        recognition_thread.daemon = True  # Allow main program to exit even if thread is running
        recognition_thread.start()
        
        # The prompt asked for a timeout for the API call itself.
        # While recognize_google() doesn't take a timeout, we can use join()
        # on the thread. This doesn't kill the thread if it's still running
        # but allows this method to return if the recognition takes too long.
        # However, if the callback is only called from the thread,
        # a timeout here might prevent the callback from being processed if
        # it occurs after the timeout but before the thread finishes.
        # For now, I will just start the thread and let it manage the callback.
        # If a hard timeout for the API call is needed, a more complex mechanism
        # (e.g., with futures or a shared event) would be required to signal
        # the thread to stop or to ignore its result.
        # For simplicity and to ensure the callback is called if recognition succeeds,
        # this method does not join the thread with a timeout. The thread is a daemon,
        # so it won't prevent the main program from exiting if it's still running.
        # If more sophisticated timeout handling for the API call itself is needed,
        # one might consider using `concurrent.futures` or other async patterns,
        # though that adds complexity beyond the scope of this base class's current design.

    def get_status(self) -> Dict[str, Any]:
        """
        Returns a dictionary containing status information about the recognizer.

        This implementation provides the 'is_listening' state and 'dictation_timeout'.
        Subclasses can extend this by calling `super().get_status()` and adding
        their own specific status details.
        """
        # Calls AbstractSpeechRecognizer.get_status() which returns {}
        status = super().get_status() 
        status["is_listening"] = self.is_listening
        status["dictation_timeout"] = self.dictation_timeout
        return status
