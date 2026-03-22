
def test_start_dictation(speech_manager):
    manager, callback = speech_manager
    manager.start_dictation()
    assert manager.is_dictating()
    manager.recognizer.start_listening.assert_called_once()

def test_stop_dictation(speech_manager):
    manager, callback = speech_manager
    manager.start_dictation()
    manager.stop_dictation()
    assert not manager.is_dictating()
    manager.recognizer.stop_listening.assert_called_once()

def test_on_transcription_valid(speech_manager):
    manager, callback = speech_manager
    manager.start_dictation()
    
    # Simulate callback from recognizer
    manager._on_transcription("Hello World")
    
    callback.assert_called_once_with("Hello World")

def test_on_transcription_empty(speech_manager):
    manager, callback = speech_manager
    manager.start_dictation()
    
    manager._on_transcription("")
    callback.assert_not_called()

def test_on_transcription_when_stopped(speech_manager):
    manager, callback = speech_manager
    # ensure it returns false
    assert not manager.is_dictating()
    
    manager._on_transcription("Late Transcription")
    callback.assert_not_called()
