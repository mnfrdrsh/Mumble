
import sys
import os

# Add src to python path
# Add src and project root to python path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
project_root = os.path.abspath(os.path.join(src_path, '..'))
sys.path.insert(0, src_path)
sys.path.insert(0, project_root)

try:
    from mumble_notes.speech_manager import SpeechManager
    print("SpeechManager imported successfully")
    
    def callback(text):
        pass
        
    sm = SpeechManager(callback)
    print("SpeechManager instantiated successfully")
    
    from mumble_notes.app import MumbleNotes
    print("MumbleNotes imported successfully")
    
except Exception as e:
    print(f"Smoke test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
