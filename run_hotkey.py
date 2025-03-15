#!/usr/bin/env python3
"""
Launcher script for the Mumble Hotkey application
"""

import os
import sys
import subprocess

def main():
    """Launch the Mumble Hotkey application"""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the mumble_hotkey.py file
    hotkey_path = os.path.join(script_dir, "src", "mumble_hotkey.py")
    
    # Check if the mumble_hotkey.py file exists
    if not os.path.exists(hotkey_path):
        print(f"Error: Could not find {hotkey_path}")
        sys.exit(1)
    
    # Launch the application
    print("Starting Mumble Hotkey Mode...")
    try:
        subprocess.run([sys.executable, hotkey_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Mumble Hotkey: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nMumble Hotkey was terminated by user.")
        sys.exit(0)

if __name__ == "__main__":
    main() 