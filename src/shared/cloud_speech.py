"""
Cloud-based speech recognition solutions that don't require PyAudio
"""

import os
import sys
import json
import logging
import threading
import time
import requests
import base64
from typing import Optional, Callable

class CloudSpeechRecognizer:
    """Base class for cloud speech recognition services"""
    
    def __init__(self):
        self.logger = logging.getLogger('mumble.cloud_speech')
        self._is_listening = False
        
    @property
    def is_listening(self) -> bool:
        return self._is_listening
        
    def start_listening(self, callback: Callable[[str], None]) -> None:
        raise NotImplementedError
        
    def stop_listening(self) -> None:
        self._is_listening = False

class WebAPIRecognizer(CloudSpeechRecognizer):
    """Speech recognition using Web Speech API via browser automation"""
    
    def __init__(self):
        super().__init__()
        self.html_file = None
        self._setup_web_interface()
        
    def _setup_web_interface(self):
        """Create HTML file with Web Speech API"""
        html_content = '''
<!DOCTYPE html>
<html>
<head>
    <title>Mumble Speech Recognition</title>
    <meta charset="utf-8">
</head>
<body>
    <h2>Mumble Speech Recognition</h2>
    <button id="startBtn">Start Listening</button>
    <button id="stopBtn">Stop Listening</button>
    <div id="result"></div>
    
    <script>
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        const result = document.getElementById('result');
        
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            
            recognition.continuous = true;
            recognition.interimResults = false;
            recognition.lang = 'en-US';
            
            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                result.textContent = transcript;
                
                // Send result to Python via localStorage
                localStorage.setItem('speechResult', transcript);
                localStorage.setItem('speechTimestamp', Date.now().toString());
            };
            
            recognition.onerror = function(event) {
                console.error('Speech recognition error:', event.error);
                localStorage.setItem('speechError', event.error);
            };
            
            startBtn.addEventListener('click', () => {
                recognition.start();
                startBtn.disabled = true;
                stopBtn.disabled = false;
                localStorage.setItem('speechStatus', 'listening');
            });
            
            stopBtn.addEventListener('click', () => {
                recognition.stop();
                startBtn.disabled = false;
                stopBtn.disabled = true;
                localStorage.setItem('speechStatus', 'stopped');
            });
            
        } else {
            result.textContent = 'Speech recognition not supported in this browser';
        }
    </script>
</body>
</html>
        '''
        
        # Save HTML file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            self.html_file = f.name
            
    def start_listening(self, callback: Callable[[str], None]) -> None:
        """Start listening using web browser"""
        if self._is_listening:
            return
            
        self._is_listening = True
        
        # Open browser with speech recognition
        import webbrowser
        webbrowser.open(f'file://{self.html_file}')
        
        # Start monitoring thread
        threading.Thread(
            target=self._monitor_web_results,
            args=(callback,),
            daemon=True
        ).start()
        
    def _monitor_web_results(self, callback):
        """Monitor web speech results via file/localStorage polling"""
        # This is a simplified example - real implementation would need
        # better browser automation (like Selenium)
        self.logger.info("Web speech monitoring started (manual implementation)")
        self.logger.info("Use the browser window to control speech recognition")
        
class WindowsSpeechRecognizer(CloudSpeechRecognizer):
    """Use Windows built-in speech recognition via PowerShell"""
    
    def __init__(self):
        super().__init__()
        if sys.platform != "win32":
            raise OSError("Windows Speech Recognition only available on Windows")
            
    def start_listening(self, callback: Callable[[str], None]) -> None:
        """Start Windows speech recognition"""
        if self._is_listening:
            return
            
        self._is_listening = True
        
        # Use PowerShell with Windows Speech Recognition
        powershell_script = '''
Add-Type -AssemblyName System.Speech
$recognizer = New-Object System.Speech.Recognition.SpeechRecognitionEngine
$recognizer.SetInputToDefaultAudioDevice()
$recognizer.LoadGrammar((New-Object System.Speech.Recognition.DictationGrammar))

$recognizer.add_SpeechRecognized({
    param($sender, $e)
    Write-Output $e.Result.Text
})

$recognizer.RecognizeAsync([System.Speech.Recognition.RecognizeMode]::Multiple)
Read-Host "Press Enter to stop"
        '''
        
        threading.Thread(
            target=self._run_powershell_recognition,
            args=(powershell_script, callback),
            daemon=True
        ).start()
        
    def _run_powershell_recognition(self, script, callback):
        """Run PowerShell speech recognition"""
        import subprocess
        
        try:
            # Save script to temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False) as f:
                f.write(script)
                script_path = f.name
                
            # Run PowerShell script
            process = subprocess.Popen(
                ['powershell', '-ExecutionPolicy', 'Bypass', '-File', script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            while self._is_listening:
                line = process.stdout.readline()
                if line.strip() and callback:
                    callback(line.strip())
                    
        except Exception as e:
            self.logger.error(f"Windows speech recognition error: {e}")
        finally:
            try:
                os.unlink(script_path)
            except:
                pass

class KeyboardInputRecognizer(CloudSpeechRecognizer):
    """Fallback: Use keyboard input instead of speech"""
    
    def __init__(self):
        super().__init__()
        
    def start_listening(self, callback: Callable[[str], None]) -> None:
        """Start keyboard input as speech alternative"""
        if self._is_listening:
            return
            
        self._is_listening = True
        self.logger.info("Using keyboard input as speech alternative")
        print("Speech recognition unavailable. Type your text and press Enter:")
        
        threading.Thread(
            target=self._keyboard_input_loop,
            args=(callback,),
            daemon=True
        ).start()
        
    def _keyboard_input_loop(self, callback):
        """Get text input from keyboard"""
        while self._is_listening:
            try:
                text = input(">>> ")
                if text.strip() and callback:
                    callback(text.strip())
            except (EOFError, KeyboardInterrupt):
                break

# Factory function to create the best available recognizer
def create_cloud_speech_recognizer():
    """Create the best available cloud speech recognizer"""
    
    # Try Windows built-in first
    if sys.platform == "win32":
        try:
            return WindowsSpeechRecognizer()
        except Exception as e:
            logging.getLogger('mumble.cloud_speech').warning(f"Windows speech not available: {e}")
    
    # Try web-based recognition
    try:
        return WebAPIRecognizer()
    except Exception as e:
        logging.getLogger('mumble.cloud_speech').warning(f"Web speech not available: {e}")
    
    # Fallback to keyboard input
    logging.getLogger('mumble.cloud_speech').info("Using keyboard input fallback")
    return KeyboardInputRecognizer() 