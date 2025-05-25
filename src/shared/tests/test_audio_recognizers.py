"""
Tests for PyAudioRecognizer, SoundDeviceRecognizer, and indirectly BaseAudioRecognizer.
"""

import pytest
from unittest.mock import MagicMock, patch, call
import speech_recognition as sr
import numpy as np
import os # For os.environ and os.unlink
import logging
import threading # For checking thread interactions

# Classes to test
from src.shared.pyaudio_recognizer import PyAudioRecognizer
from src.shared.sounddevice_recognizer import SoundDeviceRecognizer
from src.shared.base_audio_recognizer import BaseAudioRecognizer # For direct test if needed

# Disable logging for tests unless specifically needed
# logging.disable(logging.CRITICAL) # Keep logs for debugging for now

# --- Fixtures ---

@pytest.fixture
def pyaudio_recognizer_fixture():
    """Fixture for PyAudioRecognizer."""
    with patch.dict(os.environ, {}, clear=True): # Ensure clean env for timeout tests
        recognizer = PyAudioRecognizer()
    # Mock parts of sr.Recognizer instance within the class
    # This is the recognizer instance from the speech_recognition library
    recognizer.recognizer = MagicMock(spec=sr.Recognizer)
    return recognizer

@pytest.fixture
def sounddevice_recognizer_fixture():
    """Fixture for SoundDeviceRecognizer."""
    with patch.dict(os.environ, {}, clear=True): # Clean env
        # Mock SOUNDDEVICE_AVAILABLE to be true for most tests of this fixture
        with patch('src.shared.sounddevice_recognizer.SOUNDDEVICE_AVAILABLE', True):
            # Mock sounddevice.query_devices to prevent actual hardware queries
            with patch('sounddevice.query_devices', MagicMock(return_value={'name': 'mock_device', 'max_input_channels': 1})):
                 recognizer = SoundDeviceRecognizer()
    # Mock parts of sr.Recognizer instance
    recognizer.recognizer = MagicMock(spec=sr.Recognizer)
    return recognizer

# @pytest.fixture
# def sample_audio_file(tmp_path) -> Path: # Path is not defined yet
#     """Create a sample WAV file for testing"""
#     file_path = tmp_path / "test_audio.wav"
#     # Create 1 second of silence (16KHz sample rate)
#     sample_rate = 16000
#     duration = 1  # seconds
#     samples = np.zeros(sample_rate * duration, dtype=np.int16)
#     import wave # Import wave here as it's only for this fixture
#     with wave.open(str(file_path), 'wb') as wav_file:
#         wav_file.setnchannels(1)  # Mono
#         wav_file.setsampwidth(2)  # 16-bit
#         wav_file.setframerate(sample_rate)
#         wav_file.writeframes(samples.tobytes())
#     return file_path

# --- Initialization and Configuration Tests ---

def test_pyaudio_recognizer_initialization(pyaudio_recognizer_fixture):
    recognizer = pyaudio_recognizer_fixture
    assert isinstance(recognizer.logger, logging.Logger)
    assert recognizer.logger.name == 'mumble.pyaudio_speech'
    assert isinstance(recognizer._stop_requested, threading.Event) # Check type
    assert recognizer.dictation_timeout == 5 # Default
    assert recognizer.get_name() == "pyaudio"
    assert not recognizer.is_listening # Uses the property

@patch.dict(os.environ, {"MUMBLE_DICTATION_TIMEOUT": "10"})
def test_pyaudio_recognizer_dictation_timeout_from_env():
    # No fixture used here to test constructor directly with env var
    recognizer = PyAudioRecognizer()
    assert recognizer.dictation_timeout == 10

def test_sounddevice_recognizer_initialization(sounddevice_recognizer_fixture):
    recognizer = sounddevice_recognizer_fixture
    assert isinstance(recognizer.logger, logging.Logger)
    assert recognizer.logger.name == 'mumble.sounddevice_speech'
    assert isinstance(recognizer._stop_requested, threading.Event)
    assert recognizer.dictation_timeout == 5 # Default
    assert recognizer.sample_rate == 16000 # Default specific to SoundDeviceRecognizer
    assert recognizer.channels == 1 # Default specific to SoundDeviceRecognizer
    assert recognizer.get_name() == "sounddevice"
    assert not recognizer.is_listening

@patch.dict(os.environ, {"MUMBLE_DICTATION_TIMEOUT": "7"})
def test_sounddevice_recognizer_dictation_timeout_from_env():
    with patch('src.shared.sounddevice_recognizer.SOUNDDEVICE_AVAILABLE', True):
        with patch('sounddevice.query_devices', MagicMock(return_value={'name': 'mock_device', 'max_input_channels': 1})):
            recognizer = SoundDeviceRecognizer()
    assert recognizer.dictation_timeout == 7
    
@patch('src.shared.sounddevice_recognizer.SOUNDDEVICE_AVAILABLE', False)
def test_sounddevice_recognizer_import_error_if_not_available():
    with pytest.raises(ImportError) as excinfo:
        SoundDeviceRecognizer()
    assert "SoundDevice and/or SoundFile are not installed" in str(excinfo.value)

# --- get_name() Tests --- already covered in initialization

# --- get_status() Tests ---

def test_pyaudio_recognizer_get_status(pyaudio_recognizer_fixture):
    recognizer = pyaudio_recognizer_fixture
    status = recognizer.get_status()
    assert status["is_listening"] is False
    assert status["dictation_timeout"] == 5
    # BaseAudioRecognizer.get_status() does not include 'recognizer_name'
    # It's part of AbstractSpeechRecognizer's get_status, which BaseAudioRecognizer doesn't call super() for.
    assert "recognizer_name" not in status 

def test_sounddevice_recognizer_get_status(sounddevice_recognizer_fixture):
    recognizer = sounddevice_recognizer_fixture
    status = recognizer.get_status()
    assert status["is_listening"] is False
    assert status["dictation_timeout"] == 5
    assert "recognizer_name" not in status


# --- start_listening() and stop_listening() Tests ---

@patch('src.shared.pyaudio_recognizer.sr.Microphone') # Path to Microphone within the pyaudio_recognizer module
@patch('threading.Thread') # Path to the global Thread class
def test_pyaudio_start_listening(mock_thread_class, mock_microphone_class, pyaudio_recognizer_fixture):
    recognizer = pyaudio_recognizer_fixture
    
    # Mock the context manager part of sr.Microphone
    mock_mic_instance = MagicMock()
    mock_microphone_class.return_value.__enter__.return_value = mock_mic_instance
    
    callback_fn = MagicMock()
    recognizer.start_listening(callback_fn)

    assert recognizer.is_listening is True
    assert recognizer._callback == callback_fn
    
    # recognizer.recognizer is the mocked sr.Recognizer instance from the fixture
    recognizer.recognizer.adjust_for_ambient_noise.assert_called_once_with(mock_mic_instance, duration=0.5)
    
    mock_thread_class.assert_called_once_with(target=recognizer._listen_loop, daemon=True)
    mock_thread_class.return_value.start.assert_called_once()
    assert recognizer._listen_thread == mock_thread_class.return_value

    # Test starting again while already listening
    # Reset mocks for the second call check, but instance calls like adjust_for_ambient_noise should not be called again
    mock_thread_class.reset_mock() 
    recognizer.start_listening(callback_fn) # Should log a warning and return
    
    # Ensure no new thread was started
    mock_thread_class.assert_not_called() 
    assert recognizer.recognizer.adjust_for_ambient_noise.call_count == 1 # Still 1 from the first call


def test_pyaudio_stop_listening(pyaudio_recognizer_fixture):
    recognizer = pyaudio_recognizer_fixture
    
    # Simulate that it was listening
    recognizer._is_listening_state = True 
    recognizer._listen_thread = MagicMock(spec=threading.Thread)
    recognizer._listen_thread.is_alive.return_value = True

    recognizer.stop_listening()

    assert recognizer.is_listening is False # Property should reflect internal state
    assert recognizer._stop_requested.is_set()
    recognizer._listen_thread.join.assert_called_once_with(timeout=2.0)
    assert recognizer._listen_thread is None # Should be reset

    # Test stopping when not listening (should be idempotent or log a warning)
    recognizer._stop_requested.clear() # Reset for this part of the test
    # _is_listening_state is already False
    # _listen_thread is already None
    
    # To properly test idempotency, ensure no critical actions (like join on None) happen
    with patch.object(recognizer.logger, 'warning') as mock_log_warning:
        recognizer.stop_listening()
        # If it was truly not listening (and _listen_thread is None), join shouldn't be called.
        # The previous call set _listen_thread to None.
        # If stop_listening is called when _listen_thread is None, join should not be called.
        # The mock_log_warning.assert_called_once_with("Not currently listening, stop_listening called.")
        # depends on the exact logging message which can be brittle.
        # The main thing is it doesn't crash and state remains not listening.
        assert not recognizer.is_listening

@patch('src.shared.sounddevice_recognizer.sd') # Mock the 'sd' module used by SoundDeviceRecognizer
@patch('threading.Thread')
def test_sounddevice_start_listening(mock_thread_class, mock_sd_module, sounddevice_recognizer_fixture):
    recognizer = sounddevice_recognizer_fixture
    callback_fn = MagicMock()
    
    # Prevent actual sounddevice calls if any were to slip through deeper, though _listen_loop is threaded.
    mock_sd_module.rec.return_value = MagicMock() # Dummy data for recording
    mock_sd_module.wait.return_value = None

    recognizer.start_listening(callback_fn)

    assert recognizer.is_listening is True
    assert recognizer._callback == callback_fn
    
    mock_thread_class.assert_called_once_with(target=recognizer._listen_loop, daemon=True)
    mock_thread_class.return_value.start.assert_called_once()
    assert recognizer._listen_thread == mock_thread_class.return_value
    
    # Test starting again while already listening
    mock_thread_class.reset_mock()
    recognizer.start_listening(callback_fn)
    mock_thread_class.assert_not_called() # No new thread


def test_sounddevice_stop_listening(sounddevice_recognizer_fixture):
    recognizer = sounddevice_recognizer_fixture
    
    # Simulate that it was listening
    recognizer._is_listening_state = True
    recognizer._listen_thread = MagicMock(spec=threading.Thread)
    recognizer._listen_thread.is_alive.return_value = True

    recognizer.stop_listening()

    assert recognizer.is_listening is False
    assert recognizer._stop_requested.is_set()
    recognizer._listen_thread.join.assert_called_once_with(timeout=2.0)
    assert recognizer._listen_thread is None


# --- Transcription Tests (testing _recognize_audio_with_google via subclasses) ---

@patch('src.shared.pyaudio_recognizer.sr.Microphone') # Mocks the class sr.Microphone
def test_pyaudio_speech_transcription_success(mock_microphone_class, pyaudio_recognizer_fixture):
    recognizer = pyaudio_recognizer_fixture
    mock_mic_instance = MagicMock() # This is the instance returned by sr.Microphone()
    mock_microphone_class.return_value.__enter__.return_value = mock_mic_instance
    
    # Mock the listen call to return some dummy audio data
    mock_audio_data = MagicMock(spec=sr.AudioData)
    recognizer.recognizer.listen.return_value = mock_audio_data # listen() is a method of sr.Recognizer
    
    # Mock recognize_google to return a successful transcription
    expected_text = "hello world"
    # recognize_google() is also a method of sr.Recognizer instance
    recognizer.recognizer.recognize_google.return_value = expected_text
    
    callback_fn = MagicMock()
    
    # Mock the threading.Thread to execute the _listen_loop synchronously for easier testing
    with patch('threading.Thread', MagicMock(side_effect=lambda target, daemon: MagicMock(start=lambda: target(), join=lambda timeout: None))):
        recognizer.start_listening(callback_fn) # This will run _listen_loop in the "mocked" thread

    # _listen_loop calls self.recognizer.listen() -> mock_audio_data
    # then calls self._recognize_audio_with_google(mock_audio_data, self._callback)
    # _recognize_audio_with_google then calls self.recognizer.recognize_google(mock_audio_data)
    
    recognizer.recognizer.listen.assert_called_once_with(mock_mic_instance, phrase_time_limit=recognizer.dictation_timeout, timeout=1.0)
    recognizer.recognizer.recognize_google.assert_called_once_with(mock_audio_data, show_all=False)
    callback_fn.assert_called_once_with(expected_text)


@patch('src.shared.pyaudio_recognizer.sr.Microphone')
def test_pyaudio_speech_transcription_unknown_value_error(mock_microphone_class, pyaudio_recognizer_fixture):
    recognizer = pyaudio_recognizer_fixture
    mock_mic_instance = MagicMock()
    mock_microphone_class.return_value.__enter__.return_value = mock_mic_instance
    mock_audio_data = MagicMock(spec=sr.AudioData)
    recognizer.recognizer.listen.return_value = mock_audio_data
    
    recognizer.recognizer.recognize_google.side_effect = sr.UnknownValueError("API could not understand audio")
    
    callback_fn = MagicMock()

    with patch('threading.Thread', MagicMock(side_effect=lambda target, daemon: MagicMock(start=lambda: target(), join=lambda timeout: None))):
        recognizer.start_listening(callback_fn)

    recognizer.recognizer.recognize_google.assert_called_once_with(mock_audio_data, show_all=False)
    callback_fn.assert_not_called()


@patch('src.shared.pyaudio_recognizer.sr.Microphone')
def test_pyaudio_speech_transcription_request_error(mock_microphone_class, pyaudio_recognizer_fixture):
    recognizer = pyaudio_recognizer_fixture
    mock_mic_instance = MagicMock()
    mock_microphone_class.return_value.__enter__.return_value = mock_mic_instance
    mock_audio_data = MagicMock(spec=sr.AudioData)
    recognizer.recognizer.listen.return_value = mock_audio_data
    
    recognizer.recognizer.recognize_google.side_effect = sr.RequestError("API request failed")
    
    callback_fn = MagicMock()

    with patch.object(recognizer.logger, 'error') as mock_log_error:
        with patch('threading.Thread', MagicMock(side_effect=lambda target, daemon: MagicMock(start=lambda: target(), join=lambda timeout: None))):
            recognizer.start_listening(callback_fn)

    recognizer.recognizer.recognize_google.assert_called_once_with(mock_audio_data, show_all=False)
    callback_fn.assert_not_called()
    mock_log_error.assert_any_call( # logger.error is called from _recognize_audio_with_google
        "Could not request results from Google Speech Recognition service; API request failed"
    )

@patch('src.shared.sounddevice_recognizer.sd')
@patch('src.shared.sounddevice_recognizer.sf')
@patch('src.shared.sounddevice_recognizer.tempfile.NamedTemporaryFile')
@patch('src.shared.sounddevice_recognizer.os.unlink')
@patch('src.shared.sounddevice_recognizer.sr.AudioFile')
def test_sounddevice_speech_transcription_success(
    mock_audio_file_class, mock_os_unlink, mock_tempfile, mock_sf_module, mock_sd_module,
    sounddevice_recognizer_fixture
):
    recognizer = sounddevice_recognizer_fixture
    
    # Mock sounddevice recording
    mock_sd_module.rec.return_value = np.array([0]*16000, dtype=np.int16) # Dummy audio data
    # mock_sd_module.wait.return_value = None # wait is part of rec call in current code

    # Mock tempfile creation
    mock_temp_wav_file = MagicMock()
    mock_temp_wav_file.name = "dummy_temp.wav"
    mock_tempfile.return_value.__enter__.return_value = mock_temp_wav_file
    
    # Mock sr.AudioFile context manager
    mock_audio_file_instance = MagicMock() # This is 'source' in 'with sr.AudioFile(path) as source:'
    mock_audio_file_class.return_value.__enter__.return_value = mock_audio_file_instance
    
    # Mock recognizer.record (called with the source from AudioFile)
    mock_recorded_audio_data = MagicMock(spec=sr.AudioData)
    recognizer.recognizer.record.return_value = mock_recorded_audio_data # record() is method of sr.Recognizer
    
    # Mock recognize_google for success
    expected_text = "hello sounddevice"
    recognizer.recognizer.recognize_google.return_value = expected_text
    
    callback_fn = MagicMock()

    with patch('threading.Thread', MagicMock(side_effect=lambda target, daemon: MagicMock(start=lambda: target(), join=lambda timeout: None))):
        recognizer.start_listening(callback_fn)

    # Verifications
    mock_sd_module.rec.assert_called_once() # Check if sd.rec was called
    mock_sd_module.wait.assert_called_once() # Check if sd.wait was called after rec
    mock_sf_module.write.assert_called_once_with(mock_temp_wav_file.name, mock_sd_module.rec.return_value, recognizer.sample_rate)
    mock_audio_file_class.assert_called_once_with(mock_temp_wav_file.name)
    recognizer.recognizer.record.assert_called_once_with(mock_audio_file_instance)
    recognizer.recognizer.recognize_google.assert_called_once_with(mock_recorded_audio_data, show_all=False)
    callback_fn.assert_called_once_with(expected_text)
    mock_os_unlink.assert_called_once_with(mock_temp_wav_file.name)


@patch('src.shared.sounddevice_recognizer.sd')
@patch('src.shared.sounddevice_recognizer.sf')
@patch('src.shared.sounddevice_recognizer.tempfile.NamedTemporaryFile')
@patch('src.shared.sounddevice_recognizer.os.unlink')
@patch('src.shared.sounddevice_recognizer.sr.AudioFile')
def test_sounddevice_speech_transcription_unknown_value_error(
    mock_audio_file_class, mock_os_unlink, mock_tempfile, mock_sf_module, mock_sd_module,
    sounddevice_recognizer_fixture
):
    recognizer = sounddevice_recognizer_fixture
    mock_sd_module.rec.return_value = np.array([1]*16000, dtype=np.int16) # Non-silent audio
    mock_temp_wav_file = MagicMock()
    mock_temp_wav_file.name = "dummy_temp.wav"
    mock_tempfile.return_value.__enter__.return_value = mock_temp_wav_file
    mock_audio_file_instance = MagicMock()
    mock_audio_file_class.return_value.__enter__.return_value = mock_audio_file_instance
    mock_recorded_audio_data = MagicMock(spec=sr.AudioData)
    recognizer.recognizer.record.return_value = mock_recorded_audio_data
    
    recognizer.recognizer.recognize_google.side_effect = sr.UnknownValueError()
    
    callback_fn = MagicMock()

    with patch('threading.Thread', MagicMock(side_effect=lambda target, daemon: MagicMock(start=lambda: target(), join=lambda timeout: None))):
        recognizer.start_listening(callback_fn)
    
    recognizer.recognizer.recognize_google.assert_called_once_with(mock_recorded_audio_data, show_all=False)
    callback_fn.assert_not_called()
    mock_os_unlink.assert_called_once_with(mock_temp_wav_file.name) # Ensure cleanup still happens


@patch('src.shared.sounddevice_recognizer.sd')
@patch('src.shared.sounddevice_recognizer.sf')
@patch('src.shared.sounddevice_recognizer.tempfile.NamedTemporaryFile')
@patch('src.shared.sounddevice_recognizer.os.unlink')
@patch('src.shared.sounddevice_recognizer.sr.AudioFile')
def test_sounddevice_speech_transcription_request_error(
    mock_audio_file_class, mock_os_unlink, mock_tempfile, mock_sf_module, mock_sd_module,
    sounddevice_recognizer_fixture
):
    recognizer = sounddevice_recognizer_fixture
    mock_sd_module.rec.return_value = np.array([1]*16000, dtype=np.int16) # Non-silent audio
    mock_temp_wav_file = MagicMock()
    mock_temp_wav_file.name = "dummy_temp.wav"
    mock_tempfile.return_value.__enter__.return_value = mock_temp_wav_file
    mock_audio_file_instance = MagicMock()
    mock_audio_file_class.return_value.__enter__.return_value = mock_audio_file_instance
    mock_recorded_audio_data = MagicMock(spec=sr.AudioData)
    recognizer.recognizer.record.return_value = mock_recorded_audio_data
    
    recognizer.recognizer.recognize_google.side_effect = sr.RequestError("API is down")
    
    callback_fn = MagicMock()

    with patch.object(recognizer.logger, 'error') as mock_log_error:
        with patch('threading.Thread', MagicMock(side_effect=lambda target, daemon: MagicMock(start=lambda: target(), join=lambda timeout: None))):
            recognizer.start_listening(callback_fn)
            
    recognizer.recognizer.recognize_google.assert_called_once_with(mock_recorded_audio_data, show_all=False)
    callback_fn.assert_not_called()
    mock_log_error.assert_any_call(
        "Could not request results from Google Speech Recognition service; API is down"
    )
    mock_os_unlink.assert_called_once_with(mock_temp_wav_file.name) # Ensure cleanup


# --- Noise Handling Test (PyAudio specific) ---

@patch('src.shared.pyaudio_recognizer.sr.Microphone')
def test_pyaudio_noise_handling(mock_microphone_class, pyaudio_recognizer_fixture):
    recognizer = pyaudio_recognizer_fixture
    mock_mic_instance = MagicMock()
    mock_microphone_class.return_value.__enter__.return_value = mock_mic_instance

    # The fixture already mocks recognizer.recognizer (the sr.Recognizer instance)
    
    # To prevent the thread from actually running its loop and calling listen etc.
    # we can patch the _listen_loop method itself for this specific test.
    with patch.object(recognizer, '_listen_loop', MagicMock()): # Patch instance method
      recognizer.start_listening(MagicMock()) # Call start_listening to trigger adjust_for_ambient_noise
    
    recognizer.recognizer.adjust_for_ambient_noise.assert_called_once_with(mock_mic_instance, duration=0.5)

    # Test if it's called again if start_listening is called after stop (it should be)
    recognizer.recognizer.reset_mock() # Reset call count for adjust_for_ambient_noise
    
    # Simulate stopping and starting again
    recognizer._is_listening_state = False 
    recognizer._stop_requested.clear()

    with patch.object(recognizer, '_listen_loop', MagicMock()):
        recognizer.start_listening(MagicMock())
    
    recognizer.recognizer.adjust_for_ambient_noise.assert_called_once_with(mock_mic_instance, duration=0.5)


# --- Test specific BaseAudioRecognizer logic ---

from typing import Callable # Ensure Callable is imported for MinimalRecognizer

class MinimalRecognizer(BaseAudioRecognizer):
    """Minimal concrete subclass for testing BaseAudioRecognizer protected methods."""
    def __init__(self, logger_name="mumble.minimal_test"):
        super().__init__(logger_name)
    def start_listening(self, callback: Callable[[str], None]) -> None: self._is_listening_state = True
    def stop_listening(self) -> None: self._is_listening_state = False
    def get_name(self) -> str: return "minimal"
    # is_listening property is inherited and uses _is_listening_state

def test_base_audio_recognizer_recognize_google_request_error():
    """Test that _recognize_audio_with_google logs sr.RequestError correctly."""
    recognizer = MinimalRecognizer()
    # The recognizer.recognizer (sr.Recognizer instance) is part of BaseAudioRecognizer's __init__
    # We need to mock it on the instance *after* BaseAudioRecognizer.__init__ has run.
    recognizer.recognizer = MagicMock(spec=sr.Recognizer) 
    
    recognizer.recognizer.recognize_google.side_effect = sr.RequestError("API request failed")
    
    mock_audio_data = MagicMock(spec=sr.AudioData)
    callback_fn = MagicMock()
    
    # _recognize_audio_with_google runs in a thread, mock thread to run synchronously
    with patch('threading.Thread', MagicMock(side_effect=lambda target, daemon: MagicMock(daemon=True, start=lambda: target()))):
         with patch.object(recognizer.logger, 'error') as mock_log_error:
            recognizer._recognize_audio_with_google(mock_audio_data, callback_fn) # Call the method to test

    recognizer.recognizer.recognize_google.assert_called_once_with(mock_audio_data, show_all=False)
    callback_fn.assert_not_called()
    mock_log_error.assert_called_once_with(
        "Could not request results from Google Speech Recognition service; API request failed"
    )

# Final cleanup of old commented tests (removing all lines that start with '# def test_')
# This will be done by removing blocks of commented tests.
# For example, removing '# def test_language_setting(recognizer): ...' and its content.
# The following commented lines are placeholders for the actual commented out tests.
# Final cleanup of old commented tests
# All old test functions that were commented out (e.g., test_language_setting, test_ambient_duration_setting, etc.)
# are now physically removed from the file.