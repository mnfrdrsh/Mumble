#!/usr/bin/env python3
"""
Launcher script for the Mumble application
"""

import os
import sys
import subprocess

def main():
    """Launch the Mumble application"""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the main.py file
    main_path = os.path.join(script_dir, "src", "main.py")
    
    # Check if the main.py file exists
    if not os.path.exists(main_path):
        print(f"Error: Could not find {main_path}")
        sys.exit(1)
    
    # Launch the application
    print("Starting Mumble...")
    try:
        subprocess.run([sys.executable, main_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Mumble: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nMumble was terminated by user.")
        sys.exit(0)

if __name__ == "__main__":
    main() 