# Mumble


Mumble is a lightweight, open-source speech-to-text application for desktop that transcribes audio from your microphone and inserts it into any active text field using simple hotkeys. Inspired by tools like Wispr Flow, Mumble features a minimal listening bar with a squiggly line animation to provide visual feedback during recording.

## Features

-   Speech-to-Text: Transcribes spoken words into text using Google Speech Recognition.

-   Hotkey Support: Hold Ctrl + Alt to start recording and release either key to stop and insert text.

-   Visual Feedback: A small, draggable listening bar with a squiggly line that animates during recording.

-   Cross-Application Integration: Inserts transcribed text into any focused text field (e.g., Notepad, Word, browsers).

-   System Tray: Runs unobtrusively with a system tray icon for easy status monitoring and exit.

-   Configurable: Customize hotkeys, sounds, and bar position via a config.ini file.

-   Platform Support: Works on Windows, macOS, and Linux (with some setup considerations).


# Installation

## Prerequisites

-   Python: Version 3.6 or later ([Download](https://www.python.org/downloads/)).

-   Microphone: A working microphone (built-in or external).

-   Internet Connection: Required for Google Speech Recognition.

## Steps

1.  Clone the Repository:

    bash

    ```
    git clone <your-repo>
    cd <your-repo>
    ```

2.  Install Dependencies: Create a virtual environment (optional but recommended) and install required libraries:

    bash

    ```
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

    The requirements.txt file should contain:

    ```
    SpeechRecognition
    PyAudio
    keyboard
    pyperclip
    pyautogui
    pillow
    pystray
    ```

3.  Platform-Specific Setup:

    -   Windows: No additional setup typically needed.

    -   macOS: Grant accessibility permissions for keyboard and pyautogui in System Preferences > Security & Privacy > Privacy > Accessibility.

    -   Linux: Install portaudio for PyAudio:

        bash

        ```
        sudo apt-get install portaudio19-dev  # Debian/Ubuntu
        ```

        Run with sudo if hotkeys don't work:

        bash

        ```
        sudo python mumble.py
        ```


## Usage

1.  Run the Application:

    bash

    ```
    python mumble.py
    ```

2.  Interact with Mumble:

    -   A small listening bar with a gray squiggly line appears on the screen.

    -   Start Recording: Hold Ctrl + Alt. The squiggly line turns green and animates.

    -   Stop Recording: Release either Ctrl or Alt. The transcribed text is inserted into the active text field, and the line returns to gray.

    -   Move the Bar: Click and drag the listening bar to reposition it. The position is saved automatically.

    -   Exit: Right-click the system tray icon and select "Exit," or press Ctrl + C in the terminal.

3.  Example:

    -   Open Notepad and click inside it.

    -   Hold Ctrl + Alt, say "Hello from Mumble," and release Ctrl.

    -   "Hello from Mumble" appears in Notepad.


## Configuration

Mumble uses a config.ini file in the project directory for customization. If it doesn't exist, it's created with defaults on first run.

Sample config.ini

ini

```
[hotkeys]
start_hotkey = ctrl+alt

[sound]
enable_sounds = True
start_frequency = 880
start_duration = 200
stop_frequency = 440
stop_duration = 200

[behavior]
max_recording_time = 60

[gui]
bar_position_x = 50
bar_position_y = 50
```

## Options

-   hotkeys:

    -   start_hotkey: Key combination to start recording (e.g., ctrl+shift).

-   sound:

    -   enable_sounds: Toggle notification sounds (True/False).

    -   start_frequency/start_duration: Frequency (Hz) and duration (ms) of the start sound.

    -   stop_frequency/stop_duration: Frequency (Hz) and duration (ms) of the stop sound.

-   behavior:

    -   max_recording_time: Maximum recording duration in seconds (0 for unlimited).

-   gui:

    -   bar_position_x/bar_position_y: Saved position of the listening bar.

Edit config.ini to customize these settings before running the app.



## Troubleshooting

-   Hotkeys Not Working:

    -   Linux: Run with sudo python mumble.py if keyboard permissions are restricted.

    -   macOS: Ensure accessibility permissions are granted for Python in System Preferences.

    -   Conflicts: Check for other apps using Ctrl + Alt. Change start_hotkey in config.ini if needed.

-   No Audio Detected:

    -   Verify your microphone is connected and set as the default input device.

    -   Ensure PyAudio is installed correctly (pip install PyAudio).

-   Text Not Inserting:

    -   Focus a text field before using hotkeys.

    -   On macOS, confirm pyautogui has accessibility permissions.

-   Dragging Issues:

    -   Ensure config.ini is writable in the project directory.

    -   Check console output for errors during dragging.

For additional help, check the console output or open an issue on GitHub.



# Contributing

We welcome contributions! Follow these steps:

1.  Fork the Repository: Click "Fork" on GitHub to create your own copy.

2.  Create a Branch:

    bash

    ```
    git checkout -b feature/your-feature-name
    ```

3.  Make Changes: Implement your feature or fix, following Python PEP 8 style guidelines.

4.  Test: Ensure your changes work across supported platforms (Windows, macOS, Linux).

5.  Commit and Push:

    bash

    ```
    git commit -m "Add your feature description"
    git push origin feature/your-feature-name
    ```

6.  Submit a Pull Request: Open a PR on GitHub with a clear description of your changes.

See CONTRIBUTING.md for more details (create this file if needed).


# License

Mumble is licensed under the MIT License (LICENSE). Feel free to use, modify, and distribute it as you see fit.

* * * * *


# Acknowledgments

-   Built with [SpeechRecognition](https://pypi.org/project/SpeechRecognition/) and [PyAudio](https://pypi.org/project/PyAudio/).

-   Inspired by Wispr Flow's intuitive design.

-   Thanks to the open-source community for the libraries powering Mumble.

* * * * *
