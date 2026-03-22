from pathlib import Path

from setuptools import find_namespace_packages, setup


PROJECT_ROOT = Path(__file__).resolve().parent
README_PATH = PROJECT_ROOT / "README.md"


setup(
    name="mumble",
    version="2.0.0",
    description="Qt-first desktop speech-to-text application for notes and quick dictation",
    long_description=README_PATH.read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    py_modules=["modern_mumble_launcher"],
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src"),
    include_package_data=True,
    python_requires=">=3.10",
    install_requires=[
        "SpeechRecognition>=3.8.1",
        "PyQt5>=5.15",
        "sounddevice>=0.5.5",
        "keyboard>=0.13.5",
        "pyperclip>=1.8.2",
        "pyautogui>=0.9.53",
        "Pillow>=10.0.0",
    ],
    entry_points={
        "console_scripts": [
            "mumble=modern_mumble_launcher:main",
            "mumble-modern=modern_mumble_launcher:main",
        ],
    },
)
