import keyboard
import time

print("Testing keyboard module...")
print("Registering hotkey Ctrl+Alt+T")

def on_hotkey():
    print("Hotkey detected! Success!")

try:
    # Register a test hotkey
    keyboard.add_hotkey('ctrl+alt+t', on_hotkey, suppress=True)
    print("Hotkey registered. Press Ctrl+Alt+T to test within the next 30 seconds...")
    
    # Wait for 30 seconds to allow testing
    timeout = time.time() + 30
    while time.time() < timeout:
        time.sleep(1)
        
    print("Test completed. If you didn't see 'Hotkey detected!', the keyboard module may not be working correctly.")
    
except Exception as e:
    print(f"Error registering hotkey: {e}")
    
print("Test finished.") 