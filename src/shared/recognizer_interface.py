"""
Defines the AbstractSpeechRecognizer interface for all speech recognition engines.
"""
import abc
from typing import Any, Callable, Dict

class AbstractSpeechRecognizer(abc.ABC):
    """
    Abstract base class for speech recognizer implementations.

    This interface defines the common methods and properties that
    all speech recognizer implementations should provide.
    """

    @abc.abstractmethod
    def start_listening(self, callback: Callable[[str], None]) -> None:
        """
        Starts the speech recognition process.

        The recognizer will call the provided callback function with
        the recognized speech as a string.

        Args:
            callback: A function to be called when speech is recognized.
        """
        pass

    @abc.abstractmethod
    def stop_listening(self) -> None:
        """
        Stops the speech recognition process.
        """
        pass

    @property
    @abc.abstractmethod
    def is_listening(self) -> bool:
        """
        Abstract property that returns True if the recognizer is currently listening,
        False otherwise.
        """
        pass

    @abc.abstractmethod
    def get_name(self) -> str:
        """
        Returns a unique string name for the recognizer implementation.

        Examples: "pyaudio", "sounddevice".
        """
        pass

    def get_status(self) -> Dict[str, Any]:
        """
        Returns a dictionary containing status information about the recognizer.

        Subclasses can override this method to provide specific status details.
        By default, it returns an empty dictionary.
        """
        return {}
