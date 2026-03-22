"""
Deterministic quick dictation controller for the modern Qt app.
"""

from __future__ import annotations

import logging
import threading
from typing import Callable, Optional

from PyQt5.QtCore import QObject, pyqtSignal
import speech_recognition as sr

try:
    import sounddevice as sd
except ImportError:  # pragma: no cover - exercised via runtime availability checks
    sd = None


class QuickDictationController(QObject):
    """Capture microphone audio, then transcribe it after an explicit stop."""

    transcription_ready = pyqtSignal(str)
    transcription_failed = pyqtSignal(str)
    state_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("mumble.quick_dictation")
        self.channels = 1
        self.sample_width = 2
        self.sample_rate = 16000
        self._buffer = bytearray()
        self._buffer_lock = threading.Lock()
        self._stream = None
        self._callback: Optional[Callable[[str], None]] = None
        self._is_recording = False
        self._is_transcribing = False
        self._transcription_thread: Optional[threading.Thread] = None

        self.transcription_ready.connect(self._forward_transcription)

    @property
    def is_available(self) -> bool:
        """Return whether the quick dictation backend is available."""
        return sd is not None

    @property
    def is_listening(self) -> bool:
        """Compatibility alias for the active recording state."""
        return self._is_recording

    @property
    def is_transcribing(self) -> bool:
        """Return whether a completed recording is being transcribed."""
        return self._is_transcribing

    @property
    def is_busy(self) -> bool:
        """Return whether the controller is recording or transcribing."""
        return self._is_recording or self._is_transcribing

    @property
    def backend_name(self) -> str:
        """Return the user-facing backend label."""
        return "sounddevice"

    def start_listening(self, callback: Callable[[str], None]) -> None:
        """Start recording microphone audio until explicitly stopped."""
        if not self.is_available:
            raise RuntimeError("Quick dictation requires the sounddevice package.")
        if self.is_busy:
            self.logger.info("Quick dictation start requested while already busy.")
            return

        device_info = sd.query_devices(kind="input")
        default_sample_rate = device_info.get("default_samplerate", self.sample_rate)
        self.sample_rate = int(default_sample_rate) if default_sample_rate else self.sample_rate
        self._callback = callback

        with self._buffer_lock:
            self._buffer = bytearray()

        self._stream = sd.RawInputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="int16",
            callback=self._capture_audio,
        )
        self._stream.start()
        self._is_recording = True
        self.state_changed.emit("recording")
        self.logger.info("Quick dictation recording started")

    def stop_listening(self) -> None:
        """Stop recording and transcribe the captured audio."""
        if not self._is_recording:
            return

        audio_bytes = self._stop_stream(discard=False)
        duration_seconds = self._audio_duration_seconds(audio_bytes)
        if duration_seconds < 0.25:
            self.logger.info("Quick dictation stopped without enough audio to transcribe")
            self.transcription_failed.emit("No speech captured.")
            self.state_changed.emit("idle")
            return

        self._is_transcribing = True
        self.state_changed.emit("transcribing")
        self._transcription_thread = threading.Thread(
            target=self._transcribe_audio,
            args=(audio_bytes, self.sample_rate),
            daemon=True,
        )
        self._transcription_thread.start()
        self.logger.info("Quick dictation recording stopped; transcription started")

    def cancel_listening(self) -> None:
        """Stop recording and discard any captured audio."""
        if self._is_recording:
            self._stop_stream(discard=True)
        self.state_changed.emit("idle")
        self.logger.info("Quick dictation cancelled")

    def _capture_audio(self, indata, frames, time_info, status):
        """Collect raw PCM audio from the sounddevice stream callback."""
        del frames
        del time_info

        if status:
            self.logger.warning(f"Quick dictation stream status: {status}")

        with self._buffer_lock:
            self._buffer.extend(indata)

    def _stop_stream(self, discard: bool) -> bytes:
        """Stop and close the recording stream, returning captured audio."""
        stream = self._stream
        self._stream = None

        if stream is not None:
            try:
                stream.stop()
            finally:
                stream.close()

        with self._buffer_lock:
            audio_bytes = bytes(self._buffer)
            self._buffer.clear()

        self._is_recording = False
        if discard:
            return b""
        return audio_bytes

    def _transcribe_audio(self, audio_bytes: bytes, sample_rate: int) -> None:
        """Transcribe captured PCM audio in a background thread."""
        recognizer = sr.Recognizer()
        try:
            audio_data = sr.AudioData(audio_bytes, sample_rate, self.sample_width)
            text = recognizer.recognize_google(audio_data, show_all=False).strip()
            if text:
                self.transcription_ready.emit(text)
            else:
                self.transcription_failed.emit("No speech recognized.")
        except sr.UnknownValueError:
            self.transcription_failed.emit("No speech recognized.")
        except sr.RequestError as exc:
            self.transcription_failed.emit(f"Speech service unavailable: {exc}")
        except Exception as exc:  # pragma: no cover - defensive runtime path
            self.transcription_failed.emit(f"Dictation failed: {exc}")
        finally:
            self._is_transcribing = False
            self.state_changed.emit("idle")

    def _forward_transcription(self, text: str) -> None:
        """Deliver a successful transcription to the registered callback."""
        if self._callback:
            self._callback(text)

    def _audio_duration_seconds(self, audio_bytes: bytes) -> float:
        """Calculate the duration of the captured PCM bytes."""
        if not audio_bytes:
            return 0.0
        bytes_per_second = self.sample_rate * self.sample_width * self.channels
        return len(audio_bytes) / bytes_per_second
