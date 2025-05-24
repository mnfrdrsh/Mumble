#!/usr/bin/env python3
"""
Simple test script to verify Mumble applications can start
"""

import subprocess
import sys
import time
import os

def test_app(app_name, script_path):
    """Test if an application can start without errors"""
    print(f"\nTesting {app_name}...")
    
    if not os.path.exists(script_path):
        print(f"❌ {app_name}: Script not found at {script_path}")
        return False
    
    try:
        # Start the process
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it a moment to start
        time.sleep(2)
        
        # Check if it's still running
        if process.poll() is None:
            print(f"✅ {app_name}: Started successfully (PID: {process.pid})")
            process.terminate()
            process.wait(timeout=5)
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ {app_name}: Exited with code {process.returncode}")
            if stderr:
                print(f"   Error: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ {app_name}: Failed to start - {e}")
        return False

def main():
    print("Testing Mumble Applications...")
    
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Test Mumble Notes
    notes_path = os.path.join(script_dir, "src", "mumble_notes", "app.py")
    notes_ok = test_app("Mumble Notes", notes_path)
    
    # Test Mumble Quick
    quick_path = os.path.join(script_dir, "src", "mumble_quick", "app.py")
    quick_ok = test_app("Mumble Quick", quick_path)
    
    print("\n" + "="*50)
    if notes_ok and quick_ok:
        print("✅ All applications can start successfully!")
        print("\nUsage:")
        print("- Run 'python src/launcher.py' to use the launcher")
        print("- Mumble Notes will show a window when started")
        print("- Mumble Quick runs hidden, press Ctrl+Alt to activate")
    else:
        print("❌ Some applications failed to start")
        print("Check the logs in src/logs/ for more details")

if __name__ == "__main__":
    main() 