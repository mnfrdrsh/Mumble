#!/usr/bin/env python3
"""
Quick audio diagnostic script
"""

import sys

def test_pyaudio():
    """Test PyAudio"""
    print("Testing PyAudio...")
    try:
        import pyaudio
        pa = pyaudio.PyAudio()
        device_count = pa.get_device_count()
        input_devices = 0
        
        for i in range(device_count):
            device_info = pa.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                input_devices += 1
                print(f"  Input device: {device_info['name']}")
        
        pa.terminate()
        
        if input_devices > 0:
            print("✅ PyAudio working!")
            return True
        else:
            print("⚠️ PyAudio installed but no input devices")
            return False
            
    except ImportError:
        print("❌ PyAudio not installed")
        return False
    except Exception as e:
        print(f"❌ PyAudio error: {e}")
        return False

def test_sounddevice():
    """Test sounddevice"""
    print("\nTesting sounddevice...")
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        
        for device in input_devices[:3]:
            print(f"  Input device: {device['name']}")
        
        if input_devices:
            print("✅ sounddevice working!")
            return True
        else:
            print("⚠️ sounddevice installed but no input devices")
            return False
            
    except ImportError:
        print("❌ sounddevice not installed")
        return False
    except Exception as e:
        print(f"❌ sounddevice error: {e}")
        return False

def test_speech_recognition():
    """Test SpeechRecognition library"""
    print("\nTesting SpeechRecognition...")
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        print("✅ SpeechRecognition library working!")
        return True
    except ImportError:
        print("❌ SpeechRecognition not installed")
        return False
    except Exception as e:
        print(f"❌ SpeechRecognition error: {e}")
        return False

def main():
    print("🎯 Mumble Audio Diagnostic")
    print("=" * 30)
    
    pyaudio_ok = test_pyaudio()
    sounddevice_ok = test_sounddevice()
    sr_ok = test_speech_recognition()
    
    print("\n" + "=" * 30)
    print("SUMMARY:")
    
    if pyaudio_ok and sr_ok:
        print("✅ Original PyAudio setup should work")
    elif sounddevice_ok and sr_ok:
        print("✅ sounddevice alternative should work")
        print("💡 Run: pip install -r requirements_alternative.txt")
    elif sr_ok:
        print("⚠️ SpeechRecognition available but no audio backend")
        print("💡 Run: python fix_audio.py")
    else:
        print("❌ No working audio setup found")
        print("💡 Run: python fix_audio.py")
    
    print("\nRecommendations:")
    if not pyaudio_ok and not sounddevice_ok:
        print("1. Try: python fix_audio.py")
        print("2. Check microphone permissions")
        print("3. Try running as administrator")

if __name__ == "__main__":
    main() 