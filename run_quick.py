#!/usr/bin/env python3
"""
Launcher script for Mumble Quick application
"""

import os
import sys
import subprocess
import pkg_resources
import logging
from datetime import datetime

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)

def check_dependencies():
    """Verify all required dependencies are installed"""
    required = {'speech_recognition', 'keyboard', 'pyperclip', 'pyautogui', 'pystray'}
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = required - installed
    
    if missing:
        print("Error: Missing required dependencies:")
        for pkg in missing:
            print(f"  - {pkg}")
        print("\nPlease install missing dependencies:")
        print("pip install -r requirements.txt")
        sys.exit(1)

def setup_logging():
    """Set up logging configuration"""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"mumble_quick_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return log_file

def check_config():
    """Verify configuration files exist"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "src", "mumble_quick", "config", "quick_config.json")
    
    if not os.path.exists(config_path):
        print(f"Warning: Configuration file not found at {config_path}")
        print("A new configuration file will be created with default settings.")

def check_assets():
    """Verify required assets are present"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, "src", "assets")
    
    if not os.path.exists(assets_dir):
        print(f"Error: Assets directory not found at {assets_dir}")
        sys.exit(1)

def check_permissions():
    """Check for necessary system permissions"""
    try:
        import keyboard
        keyboard.hook(lambda _: None)
        keyboard.unhook_all()
    except Exception as e:
        print("Error: Unable to access keyboard. Admin privileges may be required.")
        print(f"Details: {e}")
        sys.exit(1)

def main():
    """Launch the Mumble Quick application"""
    # Set up logging
    log_file = setup_logging()
    logging.info("Starting Mumble Quick launcher")
    
    try:
        # Perform pre-launch checks
        check_python_version()
        check_dependencies()
        check_config()
        check_assets()
        check_permissions()
        
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        app_path = os.path.join(script_dir, "src", "mumble_quick", "app.py")
        
        if not os.path.exists(app_path):
            logging.error(f"Could not find {app_path}")
            print(f"Error: Could not find {app_path}")
            print("Please verify the installation directory structure.")
            sys.exit(1)
        
        # Launch the application
        print("Starting Mumble Quick...")
        logging.info("Launching application")
        
        subprocess.run([sys.executable, app_path], check=True)
        
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running Mumble Quick: {e}")
        print(f"Error running Mumble Quick: {e}")
        print(f"Check the log file for details: {log_file}")
        sys.exit(1)
    except KeyboardInterrupt:
        logging.info("Application terminated by user")
        print("\nMumble Quick was terminated by user.")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        print(f"An unexpected error occurred: {e}")
        print(f"Check the log file for details: {log_file}")
        sys.exit(1)

if __name__ == "__main__":
    main() 