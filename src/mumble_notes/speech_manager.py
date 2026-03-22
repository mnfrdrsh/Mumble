"""
Speech Manager module for handling speech recognition state and operations.
"""
import logging
from shared.adaptive_speech import create_adaptive_speech_recognizer

class SpeechManager:
    """
    Manages speech recognition for the Mumble Notes application.
    """
    def __init__(self, on_transcription_callback):
        """
        Initialize the speech manager.
        
        Args:
            on_transcription_callback (callable): Function to call with transcribed text.
        """
        self.logger = logging.getLogger('mumble.notes.speech_manager')
        self.recognizer = create_adaptive_speech_recognizer()
        self._is_dictating = False
        self.on_transcription_callback = on_transcription_callback

    def start_dictation(self):
        """Start listening for speech."""
        if not self._is_dictating:
            self._is_dictating = True
            try:
                self.recognizer.start_listening(self._on_transcription)
                self.logger.info("Started dictation")
            except Exception as e:
                self.logger.error(f"Failed to start dictation: {e}")
                self._is_dictating = False
                raise

    def stop_dictation(self):
        """Stop listening for speech."""
        if self._is_dictating:
            self._is_dictating = False
            try:
                self.recognizer.stop_listening()
                self.logger.info("Stopped dictation")
            except Exception as e:
                self.logger.error(f"Error stopping dictation: {e}")

    def _on_transcription(self, text: str):
        """Internal callback to handle transcription."""
        if text and self._is_dictating:
            self.logger.info(f"Received transcription: {text}")
            self.on_transcription_callback(text)

    def is_dictating(self) -> bool:
        """Return whether dictation is currently active."""
        return self._is_dictating
