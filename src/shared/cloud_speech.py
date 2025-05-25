"""
Provides alternative speech recognition solutions that do not rely on PyAudio or SoundDevice.

This module includes:
- `CloudSpeechRecognizer`: An abstract base for recognizers that might use cloud services
  or other non-microphone-lib-based mechanisms.
- `WebAPIRecognizer`: Uses a local HTML/JavaScript interface opened in a web browser,
  leveraging the browser's Web Speech API.
- `WindowsSpeechRecognizer`: Utilizes Windows' built-in speech recognition via PowerShell.
- `KeyboardInputRecognizer`: A fallback option that takes keyboard input as a substitute for speech.
"""

import os
import sys
# import json # Not used
import logging
import threading
import time # Used by WebAPIRecognizer
# import requests # Not used
# import base64  # Not used
import tempfile # Used by WebAPIRecognizer and WindowsSpeechRecognizer
import webbrowser # Used by WebAPIRecognizer
import subprocess # Used by WindowsSpeechRecognizer
from typing import Optional, Callable, Dict, Any
import abc # For AbstractSpeechRecognizer

from src.shared.recognizer_interface import AbstractSpeechRecognizer

class CloudSpeechRecognizer(AbstractSpeechRecognizer):
    """
    Base class for cloud or alternative speech recognition services.
    Inherits from AbstractSpeechRecognizer.
    """
    
    def __init__(self, logger_name: str = 'mumble.cloud_speech_base'):
        """
        Initializes the CloudSpeechRecognizer.

        Args:
            logger_name: The name for the logger instance.
        """
        # super().__init__() # AbstractSpeechRecognizer's __init__ does nothing.
        self.logger = logging.getLogger(logger_name)
        self._is_listening_state: bool = False # Backing variable for the is_listening property
        
    @property
    def is_listening(self) -> bool:
        """
        Indicates if the recognizer is currently listening.
        This is a concrete implementation of the abstract property.
        """
        return self._is_listening_state
        
    @abc.abstractmethod # Keep abstract as per interface, concrete classes must implement fully
    def start_listening(self, callback: Callable[[str], None]) -> None:
        """
        Starts the speech recognition process.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement start_listening.")
        
    def stop_listening(self) -> None:
        """
        Stops the speech recognition process.
        Subclasses should override to perform specific cleanup.
        """
        self.logger.info(f"Stopping recognizer: {self.get_name()}")
        self._is_listening_state = False # General stop logic

    @abc.abstractmethod # Keep abstract as per interface
    def get_name(self) -> str:
        """
        Returns a unique string name for the recognizer implementation.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement get_name.")

    def get_status(self) -> Dict[str, Any]:
        """
        Returns a dictionary containing status information about the recognizer.
        """
        return {
            "recognizer_name": self.get_name(),
            "is_listening": self.is_listening,
        }

class WebAPIRecognizer(CloudSpeechRecognizer):
    """
    Speech recognition using Web Speech API via a local HTML file opened in a browser.
    The browser handles the actual speech recognition.
    Communication is one-way (browser to Python) via localStorage polling in this example,
    meaning Python cannot directly read `localStorage` without browser automation tools
    like Selenium, which are not used here for simplicity. The user interacts with the
    HTML page in their browser to start/stop recognition.
    """
    
    def __init__(self):
        """Initializes the WebAPIRecognizer."""
        super().__init__(logger_name='mumble.web_api_speech')
        self.html_file_path: Optional[str] = None
        self._monitor_thread: Optional[threading.Thread] = None
        self._callback: Optional[Callable[[str], None]] = None
        # self._last_processed_timestamp: float = 0.0 # This was not used.
        self._setup_web_interface()
        
    def _setup_web_interface(self):
        """
        Creates a temporary HTML file that uses the Web Speech API.
        """
        html_content = '''
<!DOCTYPE html>
<html>
<head>
    <title>Mumble Speech Recognition</title>
    <meta charset="utf-8">
    <style>
        body { font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 90vh; background-color: #f0f0f0; }
        h2 { color: #333; }
        button { padding: 10px 20px; font-size: 16px; margin: 5px; cursor: pointer; border: none; border-radius: 5px; }
        #startBtn { background-color: #4CAF50; color: white; }
        #stopBtn { background-color: #f44336; color: white; }
        #result, #status { margin-top: 20px; font-size: 18px; color: #555; }
    </style>
</head>
<body>
    <h2>Mumble Web Speech API</h2>
    <p>Control listening using the buttons below. Recognized text will be sent to Mumble.</p>
    <button id="startBtn">Start Listening</button>
    <button id="stopBtn" disabled>Stop Listening</button>
    <div id="status">Status: Idle</div>
    <div id="result">Last recognized: ---</div>
    
    <script>
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        const resultDiv = document.getElementById('result');
        const statusDiv = document.getElementById('status');
        
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            
            recognition.continuous = true; // Keep listening even after a pause
            recognition.interimResults = false; // We only want final results
            recognition.lang = 'en-US'; // TODO: Make configurable
            
            recognition.onstart = function() {
                statusDiv.textContent = 'Status: Listening...';
                localStorage.setItem('mumbleSpeechStatus', 'listening');
            };

            recognition.onend = function() {
                statusDiv.textContent = 'Status: Stopped.';
                startBtn.disabled = false;
                stopBtn.disabled = true;
                localStorage.setItem('mumbleSpeechStatus', 'stopped');
            };
            
            recognition.onresult = function(event) {
                let final_transcript = '';
                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        final_transcript += event.results[i][0].transcript;
                    }
                }
                if (final_transcript) {
                    resultDiv.textContent = 'Last recognized: ' + final_transcript;
                    // Send result to Python via localStorage
                    localStorage.setItem('mumbleSpeechResult', final_transcript);
                    localStorage.setItem('mumbleSpeechTimestamp', Date.now().toString());
                }
            };
            
            recognition.onerror = function(event) {
                console.error('Speech recognition error:', event.error);
                statusDiv.textContent = 'Status: Error - ' + event.error;
                localStorage.setItem('mumbleSpeechError', event.error);
            };
            
            startBtn.addEventListener('click', () => {
                recognition.start();
                startBtn.disabled = true;
                stopBtn.disabled = false;
            });
            
            stopBtn.addEventListener('click', () => {
                recognition.stop();
                // onend will handle button states
            });
            
        } else {
            resultDiv.textContent = 'Speech recognition not supported in this browser.';
            statusDiv.textContent = 'Status: Not supported.';
            startBtn.disabled = true;
            stopBtn.disabled = true;
        }
    </script>
</body>
</html>
        '''
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                self.html_file_path = f.name
            self.logger.info(f"Web API HTML interface created at: {self.html_file_path}")
        except Exception as e:
            self.logger.error(f"Failed to create Web API HTML file: {e}", exc_info=True)
            self.html_file_path = None
            
    def start_listening(self, callback: Callable[[str], None]) -> None:
        """Starts listening by opening the web browser to the HTML interface."""
        if not self.html_file_path:
            self.logger.error("HTML file for Web API not available. Cannot start listening.")
            return

        if self._is_listening_state:
            self.logger.warning("WebAPIRecognizer is already listening.")
            return
            
        self.logger.info(f"Starting WebAPIRecognizer. Opening {self.html_file_path} in browser.")
        self._is_listening_state = True
        self._callback = callback
        # self._last_processed_timestamp = time.time() * 1000 # Not used

        try:
            webbrowser.open(f'file://{os.path.realpath(self.html_file_path)}')
        except Exception as e:
            self.logger.error(f"Failed to open web browser: {e}", exc_info=True)
            self._is_listening_state = False
            return
        
        self._monitor_thread = threading.Thread(
            target=self._monitor_web_results_loop,
            daemon=True
        )
        self._monitor_thread.start()
        
    def _monitor_web_results_loop(self):
        """
        Monitors localStorage for speech results from the browser.
        This is a simplified polling mechanism. A more robust solution might use Selenium
        or a small local web server for JavaScript to push results to.
        """
        self.logger.info("Web API result monitoring loop started.")
        # This loop simulates interaction. The actual JS needs to write to localStorage.
        # For this example, we assume that the user clicks "Start Listening" in the browser page.
        # The Python side here doesn't actively poll localStorage due to browser security restrictions
        # that prevent direct access from local file:// origins or cross-origin iframes without
        # complex setups or browser automation tools (like Selenium).
        # The JavaScript in the HTML page is responsible for handling speech events.
        # This recognizer relies on the user interacting with the opened browser page.
        # The _monitor_web_results_loop primarily keeps the listening state active
        # and would be the place to implement a communication channel if one existed (e.g., polling a local server
        # that the JavaScript could post results to, or using Selenium to query localStorage).
        try:
            while self._is_listening_state:
                # Currently, this loop doesn't actively fetch results.
                # It just keeps the thread alive while _is_listening_state is true.
                # The actual "result" would have to be communicated back to the application
                # through a more complex mechanism not implemented in this basic version.
                # For instance, the JavaScript could make a fetch request to a simple local server
                # run by the Python application.
                if self._stop_requested.wait(timeout=1.0): # Check if stop was requested
                    break 
                # time.sleep(1) # Replaced by event wait
        except Exception as e: # pylint: disable=broad-except
            self.logger.error(f"Error in Web API monitoring loop: {e}", exc_info=True)
        finally:
            self.logger.info("Web API result monitoring loop stopped.")
            self._is_listening_state = False # Ensure state is false on exit


    def stop_listening(self) -> None:
        """
        Stops the WebAPIRecognizer.
        
        This signals the monitoring loop to terminate. It does not close the browser window.
        """
        if not self._is_listening_state and not self._stop_requested.is_set(): # Added check for stop_requested
            self.logger.info("WebAPIRecognizer is not listening or already stopping.")
            # return # Allow super().stop_listening() to ensure state is correctly set

        self.logger.info("Stopping WebAPIRecognizer.")
        self._stop_requested.set() # Signal the loop to stop
        super().stop_listening() # Sets _is_listening_state to False

        if self._monitor_thread and self._monitor_thread.is_alive():
            self.logger.debug("Waiting for Web API monitor thread to join...")
            self._monitor_thread.join(timeout=1.5) # Increased timeout slightly
            if self._monitor_thread.is_alive():
                 self.logger.warning("Web API monitor thread did not join cleanly.")
        self._monitor_thread = None
        
        # Note: This does not close the browser window. The user must do that manually.
        # The temporary HTML file is cleaned up by the __del__ method.

    def get_name(self) -> str:
        """Returns the unique name for this recognizer."""
        return "web_api"

    def get_status(self) -> Dict[str, Any]:
        """Returns status information for the WebAPIRecognizer."""
        status = super().get_status()
        status["html_file_path"] = self.html_file_path
        status["monitoring_active"] = self._monitor_thread.is_alive() if self._monitor_thread else False
        return status

    def __del__(self):
        # Cleanup the temporary HTML file if it exists
        if self.html_file_path and os.path.exists(self.html_file_path):
            try:
                os.unlink(self.html_file_path)
                self.logger.info(f"Deleted temporary HTML file: {self.html_file_path}")
            except OSError as e:
                self.logger.error(f"Error deleting temporary HTML file {self.html_file_path}: {e}")


class WindowsSpeechRecognizer(CloudSpeechRecognizer):
    """
    Uses Windows built-in speech recognition via a PowerShell script.
    This recognizer is only available on Windows.
    """
    
    def __init__(self):
        """Initializes the WindowsSpeechRecognizer."""
        super().__init__(logger_name='mumble.windows_speech')
        if sys.platform != "win32":
            # This check makes the class usable (importable) on non-Windows,
            # but it will fail at runtime if instantiated.
            self.logger.warning("WindowsSpeechRecognizer initialized on non-Windows. It will not function.")
        self._process: Optional[subprocess.Popen] = None
        self._listen_thread: Optional[threading.Thread] = None
        self._temp_script_path: Optional[str] = None
        self._stop_requested = threading.Event() # Added for consistency
            
    def start_listening(self, callback: Callable[[str], None]) -> None:
        """Starts Windows speech recognition by running a PowerShell script."""
        if sys.platform != "win32":
            self.logger.error("Cannot start WindowsSpeechRecognizer: not running on Windows.")
            raise OSError("Windows Speech Recognition is only available on Windows.")

        if self._is_listening_state:
            self.logger.warning("WindowsSpeechRecognizer is already listening.")
            return

        self.logger.info("Starting WindowsSpeechRecognizer.")
        self._is_listening_state = True 
        self._stop_requested.clear() # Clear stop event
        
        powershell_script = '''
Add-Type -AssemblyName System.Speech
$recognizer = New-Object System.Speech.Recognition.SpeechRecognitionEngine
try {
    $recognizer.SetInputToDefaultAudioDevice()
} catch {
    Write-Error "Failed to set input to default audio device: $($_.Exception.Message)"
    exit 1
}
$grammar = New-Object System.Speech.Recognition.DictationGrammar
$recognizer.LoadGrammar($grammar)

$handler = {
    param($sender, $e)
    # Output recognized text to stdout
    Write-Output $e.Result.Text
    # Flush stdout to ensure Python receives it immediately
    [Console]::Out.Flush()
}
Register-ObjectEvent -InputObject $recognizer -EventName SpeechRecognized -Action $handler -MessageData "SpeechRecognized"

$recognizer.RecognizeAsync([System.Speech.Recognition.RecognizeMode]::Multiple)
Write-Host "Windows Speech Recognition started. Press Enter in the console running Mumble to stop."
# Keep the script running. Python will terminate the process to stop.
while ($true) { Start-Sleep -Seconds 1 }
        '''
        
        self._listen_thread = threading.Thread(
            target=self._run_powershell_recognition_loop,
            args=(powershell_script, callback),
            daemon=True
        )
        self._listen_thread.start()
        
    def _run_powershell_recognition_loop(self, script_content: str, callback: Callable[[str], None]):
        """
        Runs the PowerShell speech recognition script and captures its output.
        """
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False, encoding='utf-8') as f:
                self._temp_script_path = f.name
                f.write(script_content)
            
            self.logger.info(f"Executing PowerShell script: {self._temp_script_path}")
            # Using CREATE_NO_WINDOW to prevent PowerShell window from popping up
            creationflags = 0x08000000 if sys.platform == "win32" else 0 
            self._process = subprocess.Popen(
                ['powershell', '-ExecutionPolicy', 'Bypass', '-File', self._temp_script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                creationflags=creationflags
            )
            
            # Monitor stdout for recognized speech
            if self._process and self._process.stdout:
                for line in iter(self._process.stdout.readline, ''):
                    if not self._is_listening_state: # Check if stop was requested
                        break
                    line_stripped = line.strip()
                    if line_stripped and "Windows Speech Recognition started." not in line_stripped:
                        self.logger.info(f"Recognized (Windows): {line_stripped}")
                        callback(line_stripped)
                self._process.stdout.close()

            # Check for errors after process finishes or if loop breaks
            if self._process:
                return_code = self._process.wait()
                if return_code != 0:
                    stderr_output = self._process.stderr.read() if self._process.stderr else ""
                    self.logger.error(
                        f"PowerShell script exited with error code {return_code}. Stderr: {stderr_output.strip()}"
                    )
                self._process.stderr.close() if self._process.stderr else None


        except FileNotFoundError:
            self.logger.error("PowerShell executable not found. Is PowerShell installed and in PATH?")
            self._is_listening_state = False
        except Exception as e:
            self.logger.error(f"Error running Windows speech recognition: {e}", exc_info=True)
            self._is_listening_state = False # Ensure state reflects failure
        finally:
            self.logger.info("Windows PowerShell recognition loop ended.")
            if self._process: # Ensure process is terminated if it's still running
                try:
                    self._process.terminate()
                    self._process.wait(timeout=1.0)
                except subprocess.TimeoutExpired:
                    self._process.kill()
                except Exception: # pylint: disable=broad-except
                    pass # Ignore errors during cleanup
                self._process = None

            if self._temp_script_path and os.path.exists(self._temp_script_path):
                try:
                    os.unlink(self._temp_script_path)
                    self.logger.debug(f"Deleted temporary PowerShell script: {self._temp_script_path}")
                except OSError as e:
                    self.logger.error(f"Error deleting temp script {self._temp_script_path}: {e}")
                self._temp_script_path = None
            
            # If the loop exited due to an error or completion, ensure listening state is false.
            if self._is_listening_state: # If still true, means it exited unexpectedly and stop_listening wasn't called
                self.logger.warning("PowerShell recognition loop ended unexpectedly while still in listening state.")
                self._is_listening_state = False # Correct the state


    def stop_listening(self) -> None:
        """
        Stops Windows speech recognition by terminating the PowerShell script and joining the listener thread.
        """
        if not self._is_listening_state and not self._stop_requested.is_set(): # Added check for stop_requested
            self.logger.info("WindowsSpeechRecognizer is not listening or already stopping.")
            # return # Allow super().stop_listening() for state consistency

        self.logger.info("Stopping WindowsSpeechRecognizer.")
        self._stop_requested.set() # Signal the PowerShell monitoring loop to stop
        super().stop_listening() # Sets _is_listening_state to False

        if self._process and self._process.poll() is None: # Check if process is running
            self.logger.debug("Terminating PowerShell process for WindowsSpeechRecognizer.")
            try:
                # Attempt graceful termination first.
                # Sending a newline to stdin might work if Read-Host is active, but script uses while($true)
                # Forcibly terminate is more reliable here.
                self._process.terminate() 
                self._process.wait(timeout=1.0) # Wait for graceful termination
            except subprocess.TimeoutExpired:
                self.logger.warning("PowerShell process did not terminate gracefully, killing.")
                self._process.kill() # Force kill
                self._process.wait(timeout=1.0) # Wait for kill
            except Exception as e: # pylint: disable=broad-except
                self.logger.error(f"Error terminating PowerShell process: {e}", exc_info=True)
            self._process = None
        
        if self._listen_thread and self._listen_thread.is_alive():
            self.logger.debug("Waiting for Windows recognizer's PowerShell monitoring thread to join...")
            self._listen_thread.join(timeout=1.5) # Slightly increased timeout
            if self._listen_thread.is_alive():
                 self.logger.warning("Windows recognizer's PowerShell monitoring thread did not join cleanly.")
        self._listen_thread = None

        # Temporary script file cleanup is now handled in the _run_powershell_recognition_loop's finally block
        # to ensure it's cleaned up even if the thread exits unexpectedly.
        # if self._temp_script_path and os.path.exists(self._temp_script_path):
        #     try:
        #         os.unlink(self._temp_script_path)
        #     except OSError as e:
        #         self.logger.error(f"Error deleting temporary script file {self._temp_script_path}: {e}")
        #     self._temp_script_path = None


    def get_name(self) -> str:
        """Returns the unique name for this recognizer."""
        return "windows_speech"

    def get_status(self) -> Dict[str, Any]:
        """Returns status information for the WindowsSpeechRecognizer."""
        status = super().get_status()
        status["platform_supported"] = sys.platform == "win32"
        status["process_active"] = self._process is not None and self._process.poll() is None
        status["script_path"] = self._temp_script_path
        return status

class KeyboardInputRecognizer(CloudSpeechRecognizer):
    """
    Fallback recognizer that uses keyboard input instead of speech.
    Useful when no other speech recognition methods are available.
    """
    
    def __init__(self):
        """Initializes the KeyboardInputRecognizer."""
        super().__init__(logger_name='mumble.keyboard_input')
        self._input_thread: Optional[threading.Thread] = None
        self._callback: Optional[Callable[[str], None]] = None
        self._stop_requested = threading.Event() # Added for consistency
        
    def start_listening(self, callback: Callable[[str], None]) -> None:
        """Starts listening for keyboard input in a separate thread."""
        if self._is_listening_state:
            self.logger.warning("KeyboardInputRecognizer is already listening.")
            return
            
        self.logger.info("Starting KeyboardInputRecognizer. Type text and press Enter.")
        print("\n--- Keyboard Input Mode Active ---")
        print("Type your text below and press Enter. Send EOF (Ctrl+D or Ctrl+Z+Enter) or an empty line to signal potential stop if needed.")
        
        self._is_listening_state = True
        self._callback = callback
        self._stop_requested.clear() # Clear stop event
        
        self._input_thread = threading.Thread(
            target=self._keyboard_input_loop,
            daemon=True
        )
        self._input_thread.start()
        
    def _keyboard_input_loop(self):
        """Continuously prompts the user for keyboard input until stopped."""
        self.logger.debug("Keyboard input loop started.")
        while not self._stop_requested.is_set():
            try:
                # The input() call is blocking. The loop effectively checks _stop_requested
                # once per line input. If stop_listening is called, the user might need
                # to press Enter or send EOF to fully unblock the input() call and exit the loop.
                if not self._is_listening_state: # Secondary check if stop_listening was more direct
                    break
                
                # Consider using a non-blocking input method or select for more responsiveness,
                # but that adds platform-specific complexity. For CLI, this is standard.
                print("Input: ", end='', flush=True) 
                text = input() 
                
                if self._stop_requested.is_set() or not self._is_listening_state:
                    break

                if text.strip() and self._callback:
                    self.logger.info(f"Keyboard input received: '{text.strip()}'")
                    self._callback(text.strip())
                elif not text: # User just pressed Enter on an empty line
                    self.logger.debug("Empty input received, continuing to listen.")
                    # Optionally, an empty line could signify intent to stop.
                    # For now, only EOF or explicit stop_listening signals termination.

            except EOFError: # Ctrl+D (Unix) or Ctrl+Z+Enter (Windows)
                self.logger.info("EOF received, stopping keyboard input loop.")
                break 
            except KeyboardInterrupt: # Ctrl+C
                self.logger.info("KeyboardInterrupt received, stopping keyboard input loop.")
                break
            except Exception as e: # pylint: disable=broad-except
                self.logger.error(f"Error in keyboard input loop: {e}", exc_info=True)
                break # Exit loop on unexpected error
        
        self.logger.info("Keyboard input loop finished.")
        self._is_listening_state = False # Ensure state is updated on loop exit
        print("--- Exiting Keyboard Input Mode ---")


    def stop_listening(self) -> None:
        """
        Stops listening for keyboard input.
        
        Signals the input loop to terminate. The user might need to press Enter or
        send an EOF signal to fully unblock the `input()` call in the loop.
        """
        if not self._is_listening_state and not self._stop_requested.is_set():
            self.logger.info("KeyboardInputRecognizer is not listening or already stopping.")
            # return

        self.logger.info("Stopping KeyboardInputRecognizer.")
        self._stop_requested.set() # Signal the loop to stop
        super().stop_listening() # Sets _is_listening_state to False

        if self._input_thread and self._input_thread.is_alive():
            self.logger.info(
                "Keyboard input loop is active. If it doesn't stop, try pressing Enter or sending EOF (Ctrl+D / Ctrl+Z+Enter)."
            )
            self._input_thread.join(timeout=1.0) # Increased timeout slightly
            if self._input_thread.is_alive():
                self.logger.warning(
                    "Keyboard input thread did not stop quickly. It might be waiting for input."
                )
        self._input_thread = None
        

    def get_name(self) -> str:
        """Returns the unique name for this recognizer."""
        return "keyboard"

    def get_status(self) -> Dict[str, Any]:
        """Returns status information for the KeyboardInputRecognizer."""
        status = super().get_status()
        status["input_thread_active"] = self._input_thread.is_alive() if self._input_thread else False
        return status

# Factory function create_cloud_speech_recognizer() is removed as requested.