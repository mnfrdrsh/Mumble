# Mumble Installation Guide

This guide will help you install and run the Mumble speech-to-text application.

## Prerequisites

Before installing Mumble, ensure you have the following:

1. **Python 3.8 or higher**
   - Download from [python.org](https://www.python.org/downloads/)
   - Ensure Python is added to your PATH during installation

2. **Working Microphone**
   - Required for speech input
   - Test that your microphone is working properly on your system

3. **Internet Connection**
   - Required for Google's Speech Recognition service

## Installation Steps

### 1. Clone or Download the Repository

```bash
git clone https://github.com/yourusername/mumble.git
cd mumble
```

Or download and extract the ZIP file from the repository.

### 2. Create a Virtual Environment (Optional but Recommended)

#### On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

#### On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### Troubleshooting PyAudio Installation

If you encounter issues installing PyAudio:

**On Windows:**
```bash
pip install pipwin
pipwin install pyaudio
```

**On macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**On Ubuntu/Debian:**
```bash
sudo apt-get install python3-pyaudio
```

## Running the Application

### Using the Launcher Script

```bash
python run.py
```

### Running Directly

```bash
python src/main.py
```

## Verifying Installation

1. Start the application using one of the methods above
2. Click the "Start Recording" button
3. Speak into your microphone
4. You should see your speech transcribed in the text area

## Troubleshooting

### Common Issues

1. **"No module named 'speech_recognition'"**
   - Ensure you've installed the dependencies: `pip install -r requirements.txt`

2. **"Could not find PyAudio"**
   - Follow the PyAudio installation instructions above

3. **"Could not open microphone"**
   - Check that your microphone is properly connected
   - Ensure your microphone has the necessary permissions

4. **"Connection failed" or no transcription appears**
   - Check your internet connection
   - Ensure your firewall isn't blocking the application

## Getting Help

If you encounter any issues not covered in this guide, please:

1. Check the [GitHub Issues](https://github.com/yourusername/mumble/issues) for similar problems
2. Create a new issue with details about your problem 