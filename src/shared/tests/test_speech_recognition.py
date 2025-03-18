"""
Tests for shared speech recognition module
"""

import pytest
from unittest.mock import MagicMock, patch
import speech_recognition as sr
import numpy as np
from pathlib import Path
import wave
import logging

from ..speech_recognition import SpeechRecognizer

@pytest.fixture
def recognizer():
    """Create SpeechRecognizer instance"""
    return SpeechRecognizer()

@pytest.fixture
def sample_audio_file(tmp_path) -> Path:
    """Create a sample WAV file for testing"""
    file_path = tmp_path / "test_audio.wav"
    
    # Create 1 second of silence (16KHz sample rate)
    sample_rate = 16000
    duration = 1  # seconds
    samples = np.zeros(sample_rate * duration, dtype=np.int16)
    
    with wave.open(str(file_path), 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(samples.tobytes())
    
    return file_path

def test_initialization(recognizer):
    """Test recognizer initialization"""
    assert isinstance(recognizer._recognizer, sr.Recognizer)
    assert recognizer.language == 'en-US'
    assert recognizer.ambient_duration == 1.0
    assert recognizer.phrase_timeout is None
    assert recognizer.auto_stop is True
    assert recognizer.auto_stop_timeout == 2.0
    assert recognizer._is_listening is False

def test_language_setting(recognizer):
    """Test setting recognition language"""
    # Test valid language codes
    valid_languages = ['en-US', 'en-GB', 'es-ES', 'fr-FR', 'de-DE']
    for lang in valid_languages:
        recognizer.language = lang
        assert recognizer.language == lang
    
    # Test invalid language code
    with pytest.raises(ValueError):
        recognizer.language = 'invalid'

def test_ambient_duration_setting(recognizer):
    """Test setting ambient noise duration"""
    # Test valid durations
    recognizer.ambient_duration = 0.5
    assert recognizer.ambient_duration == 0.5
    
    recognizer.ambient_duration = 2.0
    assert recognizer.ambient_duration == 2.0
    
    # Test invalid durations
    with pytest.raises(ValueError):
        recognizer.ambient_duration = 0
    with pytest.raises(ValueError):
        recognizer.ambient_duration = -1

def test_phrase_timeout_setting(recognizer):
    """Test setting phrase timeout"""
    # Test valid timeouts
    recognizer.phrase_timeout = 5.0
    assert recognizer.phrase_timeout == 5.0
    
    recognizer.phrase_timeout = None
    assert recognizer.phrase_timeout is None
    
    # Test invalid timeouts
    with pytest.raises(ValueError):
        recognizer.phrase_timeout = 0
    with pytest.raises(ValueError):
        recognizer.phrase_timeout = -1

def test_auto_stop_timeout_setting(recognizer):
    """Test setting auto-stop timeout"""
    # Test valid timeouts
    recognizer.auto_stop_timeout = 1.0
    assert recognizer.auto_stop_timeout == 1.0
    
    recognizer.auto_stop_timeout = 5.0
    assert recognizer.auto_stop_timeout == 5.0
    
    # Test invalid timeouts
    with pytest.raises(ValueError):
        recognizer.auto_stop_timeout = 0
    with pytest.raises(ValueError):
        recognizer.auto_stop_timeout = -1

@patch('speech_recognition.Microphone')
def test_start_listening(mock_mic, recognizer):
    """Test starting speech recognition"""
    # Mock microphone and callback
    mock_source = MagicMock()
    mock_mic.return_value = mock_source
    callback = MagicMock()
    
    # Start listening
    recognizer.start_listening(callback)
    
    # Verify microphone setup
    mock_mic.assert_called_once()
    mock_source.__enter__.assert_called_once()
    
    # Verify recognizer state
    assert recognizer._is_listening is True
    assert recognizer._callback == callback
    
    # Verify ambient noise adjustment
    recognizer._recognizer.adjust_for_ambient_noise.assert_called_once_with(
        mock_source, duration=recognizer.ambient_duration
    )
    
    # Verify listener started
    recognizer._recognizer.listen_in_background.assert_called_once()

@patch('speech_recognition.Microphone')
def test_stop_listening(mock_mic, recognizer):
    """Test stopping speech recognition"""
    # Mock microphone and callback
    mock_source = MagicMock()
    mock_mic.return_value = mock_source
    callback = MagicMock()
    
    # Start and then stop listening
    recognizer.start_listening(callback)
    recognizer.stop_listening()
    
    # Verify recognizer state
    assert recognizer._is_listening is False
    assert recognizer._callback is None
    
    # Verify microphone cleanup
    mock_source.__exit__.assert_called_once()

def test_is_listening(recognizer):
    """Test listening state property"""
    assert recognizer.is_listening is False
    
    # Mock start_listening to set state
    recognizer._is_listening = True
    assert recognizer.is_listening is True

@patch('speech_recognition.Recognizer.recognize_google')
def test_speech_callback(mock_recognize, recognizer):
    """Test speech recognition callback"""
    # Mock successful recognition
    mock_recognize.return_value = "test text"
    callback = MagicMock()
    
    # Create audio data mock
    audio_data = MagicMock()
    
    # Process audio
    recognizer._process_audio(audio_data, callback)
    
    # Verify recognition attempt
    mock_recognize.assert_called_once_with(
        audio_data, language=recognizer.language
    )
    
    # Verify callback
    callback.assert_called_once_with("test text", None)

@patch('speech_recognition.Recognizer.recognize_google')
def test_speech_callback_error(mock_recognize, recognizer):
    """Test speech recognition error handling"""
    # Mock recognition error
    mock_recognize.side_effect = sr.UnknownValueError()
    callback = MagicMock()
    
    # Create audio data mock
    audio_data = MagicMock()
    
    # Process audio
    recognizer._process_audio(audio_data, callback)
    
    # Verify callback with error
    callback.assert_called_once_with(None, "Could not understand audio")

def test_transcribe_file(recognizer, sample_audio_file):
    """Test transcribing from audio file"""
    # Mock recognition result
    with patch.object(recognizer._recognizer, 'recognize_google',
                     return_value="test transcription"):
        result = recognizer.transcribe_file(sample_audio_file)
        assert result == "test transcription"

def test_transcribe_file_error(recognizer, sample_audio_file):
    """Test transcription error handling"""
    # Mock recognition error
    with patch.object(recognizer._recognizer, 'recognize_google',
                     side_effect=sr.UnknownValueError()):
        with pytest.raises(sr.UnknownValueError):
            recognizer.transcribe_file(sample_audio_file)

def test_auto_stop_handling(recognizer):
    """Test auto-stop functionality"""
    callback = MagicMock()
    
    # Enable auto-stop
    recognizer.auto_stop = True
    recognizer.auto_stop_timeout = 1.0
    
    # Mock silence detection
    audio_data = MagicMock()
    audio_data.get_raw_data.return_value = b'\x00' * 32000  # Silent audio
    
    # Process silent audio
    recognizer._process_audio(audio_data, callback)
    
    # Verify auto-stop triggered
    assert recognizer._is_listening is False

def test_noise_handling(recognizer):
    """Test noise level adjustment"""
    with patch('speech_recognition.Microphone') as mock_mic:
        # Mock microphone
        mock_source = MagicMock()
        mock_mic.return_value = mock_source
        
        # Start listening with different ambient durations
        recognizer.ambient_duration = 0.5
        recognizer.start_listening(MagicMock())
        
        # Verify ambient noise adjustment
        recognizer._recognizer.adjust_for_ambient_noise.assert_called_with(
            mock_source, duration=0.5
        )
        
        # Change duration and restart
        recognizer.stop_listening()
        recognizer.ambient_duration = 2.0
        recognizer.start_listening(MagicMock())
        
        # Verify new adjustment
        recognizer._recognizer.adjust_for_ambient_noise.assert_called_with(
            mock_source, duration=2.0
        ) 