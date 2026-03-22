import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# Add src and project root to path
# __file__ is src/mumble_notes/tests/conftest.py
# src is ../..
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
project_root = os.path.abspath(os.path.join(src_path, '..'))

if src_path not in sys.path:
    sys.path.insert(0, src_path)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

@pytest.fixture
def mock_recognizer():
    recognizer = MagicMock()
    return recognizer

@pytest.fixture
def speech_manager(mock_recognizer):
    with patch('mumble_notes.speech_manager.create_adaptive_speech_recognizer', return_value=mock_recognizer):
        from mumble_notes.speech_manager import SpeechManager
        # Mock callback
        callback = MagicMock()
        manager = SpeechManager(callback)
        yield manager, callback
