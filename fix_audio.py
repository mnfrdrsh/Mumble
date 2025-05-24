#!/usr/bin/env python3
"""
Comprehensive script to fix PyAudio and speech recognition issues
"""

import sys
import subprocess
import platform
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command, description="", check=True):
    """Run a command and handle errors"""
    logger.info(f"Running: {description or command}")
    try:
        result = subprocess.run(command, shell=True, check=check, 
                              capture_output=True, text=True)
        if result.stdout:
            logger.info(f"Output: {result.stdout}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Error: {e}")
        if e.stderr:
            logger.error(f"Error output: {e.stderr}")
        return False, e.stderr

def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    logger.info(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        logger.warning("Python 3.7+ recommended for best compatibility")
        return False
    return True

def check_audio_system():
    """Check system audio capabilities"""
    system = platform.system().lower()
    logger.info(f"Operating system: {system}")
    
    if system == "windows":
        # Check Windows audio
        success, output = run_command("powershell Get-WmiObject -Class Win32_SoundDevice", 
                                     "Checking Windows audio devices", check=False)
        if success and "Name" in output:
            logger.info("✅ Windows audio devices found")
            return True
        else:
            logger.warning("⚠️ No Windows audio devices detected")
            return False
    
    elif system == "linux":
        # Check ALSA/PulseAudio
        success, _ = run_command("arecord -l", "Checking Linux audio devices", check=False)
        if success:
            logger.info("✅ Linux audio devices found")
            return True
        else:
            logger.warning("⚠️ No Linux audio devices detected")
            return False
    
    elif system == "darwin":  # macOS
        # Check Core Audio
        success, _ = run_command("system_profiler SPAudioDataType", 
                                "Checking macOS audio devices", check=False)
        if success:
            logger.info("✅ macOS audio devices found")
            return True
        else:
            logger.warning("⚠️ No macOS audio devices detected")
            return False
    
    return True

def method_1_precompiled_wheels():
    """Method 1: Try precompiled wheels"""
    logger.info("\n=== Method 1: Precompiled PyAudio wheels ===")
    
    # Uninstall existing PyAudio
    run_command("pip uninstall pyaudio -y", "Uninstalling existing PyAudio", check=False)
    
    # Try pipwin (Windows)
    if platform.system().lower() == "windows":
        logger.info("Trying pipwin for Windows...")
        success, _ = run_command("pip install pipwin", "Installing pipwin", check=False)
        if success:
            success, _ = run_command("pipwin install pyaudio", "Installing PyAudio via pipwin", check=False)
            if success:
                return test_pyaudio()
    
    # Try unofficial wheels
    logger.info("Trying unofficial wheels...")
    success, _ = run_command("pip install --only-binary=all pyaudio", 
                           "Installing PyAudio (binary only)", check=False)
    if success:
        return test_pyaudio()
    
    return False

def method_2_conda():
    """Method 2: Use conda"""
    logger.info("\n=== Method 2: Conda installation ===")
    
    # Check if conda is available
    success, _ = run_command("conda --version", "Checking conda", check=False)
    if not success:
        logger.info("Conda not available, skipping this method")
        return False
    
    # Install via conda
    success, _ = run_command("conda install pyaudio -y", "Installing PyAudio via conda", check=False)
    if success:
        return test_pyaudio()
    
    return False

def method_3_sounddevice():
    """Method 3: Switch to sounddevice"""
    logger.info("\n=== Method 3: Switch to sounddevice ===")
    
    # Install sounddevice and dependencies
    packages = ["sounddevice", "soundfile", "numpy"]
    for package in packages:
        success, _ = run_command(f"pip install {package}", f"Installing {package}", check=False)
        if not success:
            logger.error(f"Failed to install {package}")
            return False
    
    return test_sounddevice()

def method_4_system_dependencies():
    """Method 4: Install system dependencies"""
    logger.info("\n=== Method 4: System dependencies ===")
    
    system = platform.system().lower()
    
    if system == "windows":
        logger.info("For Windows, install Microsoft C++ Build Tools or Visual Studio Community")
        logger.info("Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/")
        return False  # Manual installation required
    
    elif system == "linux":
        # Try different package managers
        package_managers = [
            ("apt-get", "sudo apt-get update && sudo apt-get install -y portaudio19-dev python3-pyaudio"),
            ("yum", "sudo yum install -y portaudio-devel"),
            ("dnf", "sudo dnf install -y portaudio-devel"),
            ("pacman", "sudo pacman -S portaudio")
        ]
        
        for pm, command in package_managers:
            if run_command(f"which {pm}", f"Checking {pm}", check=False)[0]:
                logger.info(f"Using {pm} package manager")
                success, _ = run_command(command, f"Installing dependencies via {pm}", check=False)
                if success:
                    # Try installing PyAudio again
                    success, _ = run_command("pip install pyaudio", "Installing PyAudio", check=False)
                    if success:
                        return test_pyaudio()
                break
    
    elif system == "darwin":  # macOS
        # Try Homebrew
        if run_command("which brew", "Checking Homebrew", check=False)[0]:
            success, _ = run_command("brew install portaudio", "Installing portaudio via Homebrew", check=False)
            if success:
                success, _ = run_command("pip install pyaudio", "Installing PyAudio", check=False)
                if success:
                    return test_pyaudio()
    
    return False

def test_pyaudio():
    """Test if PyAudio is working"""
    logger.info("Testing PyAudio...")
    try:
        import pyaudio
        
        # Try to create PyAudio instance
        pa = pyaudio.PyAudio()
        
        # Check for input devices
        device_count = pa.get_device_count()
        logger.info(f"Found {device_count} audio devices")
        
        input_devices = []
        for i in range(device_count):
            device_info = pa.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                input_devices.append(device_info['name'])
        
        logger.info(f"Input devices: {input_devices}")
        
        pa.terminate()
        
        if input_devices:
            logger.info("✅ PyAudio is working!")
            return True
        else:
            logger.warning("⚠️ PyAudio installed but no input devices found")
            return False
            
    except ImportError as e:
        logger.error(f"❌ PyAudio import failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ PyAudio test failed: {e}")
        return False

def test_sounddevice():
    """Test if sounddevice is working"""
    logger.info("Testing sounddevice...")
    try:
        import sounddevice as sd
        import numpy as np
        
        # Query devices
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        
        logger.info(f"Found {len(input_devices)} input devices")
        for device in input_devices[:3]:  # Show first 3
            logger.info(f"  - {device['name']}")
        
        if input_devices:
            logger.info("✅ sounddevice is working!")
            return True
        else:
            logger.warning("⚠️ sounddevice installed but no input devices found")
            return False
            
    except ImportError as e:
        logger.error(f"❌ sounddevice import failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ sounddevice test failed: {e}")
        return False

def update_requirements():
    """Update requirements.txt to use working audio backend"""
    logger.info("\n=== Updating requirements.txt ===")
    
    # Test what's working
    pyaudio_works = test_pyaudio()
    sounddevice_works = test_sounddevice()
    
    if pyaudio_works:
        logger.info("Using PyAudio backend")
        requirements_file = "requirements.txt"
    elif sounddevice_works:
        logger.info("Using sounddevice backend")
        requirements_file = "requirements_alternative.txt"
        # Copy alternative requirements to main file
        if os.path.exists(requirements_file):
            import shutil
            shutil.copy(requirements_file, "requirements.txt")
            logger.info("Updated requirements.txt to use sounddevice")
    else:
        logger.warning("No audio backend is working")
        return False
    
    return True

def setup_adaptive_speech():
    """Set up applications to use adaptive speech recognition"""
    logger.info("\n=== Setting up adaptive speech recognition ===")
    
    # Update import in main applications
    apps_to_update = [
        "src/mumble_notes/app.py",
        "src/mumble_quick/app.py"
    ]
    
    for app_path in apps_to_update:
        if os.path.exists(app_path):
            logger.info(f"Updating {app_path} to use adaptive speech recognition")
            
            # Read file
            with open(app_path, 'r') as f:
                content = f.read()
            
            # Replace import
            old_import = "from shared.speech_recognition import SpeechRecognizer"
            new_import = "from shared.adaptive_speech import create_adaptive_speech_recognizer as SpeechRecognizer"
            
            if old_import in content:
                content = content.replace(old_import, new_import)
                
                # Write back
                with open(app_path, 'w') as f:
                    f.write(content)
                
                logger.info(f"✅ Updated {app_path}")
            else:
                logger.info(f"No changes needed for {app_path}")
    
    return True

def main():
    """Main function to fix audio issues"""
    logger.info("🎯 Mumble Audio Fix Tool")
    logger.info("=" * 50)
    
    # Check system
    check_python_version()
    audio_available = check_audio_system()
    
    if not audio_available:
        logger.warning("⚠️ No audio devices detected. Speech recognition may not work.")
    
    # Try different methods
    methods = [
        ("Precompiled wheels", method_1_precompiled_wheels),
        ("Conda installation", method_2_conda),
        ("System dependencies", method_4_system_dependencies),
        ("sounddevice alternative", method_3_sounddevice),
    ]
    
    success = False
    for method_name, method_func in methods:
        logger.info(f"\n🔧 Trying: {method_name}")
        try:
            if method_func():
                logger.info(f"✅ {method_name} worked!")
                success = True
                break
            else:
                logger.info(f"❌ {method_name} failed")
        except Exception as e:
            logger.error(f"❌ {method_name} crashed: {e}")
    
    if success:
        logger.info("\n🎉 Audio backend is working!")
        update_requirements()
        setup_adaptive_speech()
        logger.info("\n✅ Setup complete! Try running your Mumble applications now.")
    else:
        logger.error("\n😞 All methods failed. Recommendations:")
        logger.error("1. Check if your microphone is connected and working")
        logger.error("2. Try running as administrator (Windows)")
        logger.error("3. Install Microsoft C++ Build Tools (Windows)")
        logger.error("4. Use the keyboard input fallback")
        logger.error("5. Try the web-based speech recognition")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 