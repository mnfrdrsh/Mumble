from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mumble-apps",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A suite of speech-to-text applications for note-taking and quick input",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mumble",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: News/Diary",
        "Topic :: Text Processing :: General",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "speech_recognition>=3.8.1",
        "pillow>=8.0.0",
        "pytest>=6.0.0",
        "keyboard>=0.13.5",
        "pyperclip>=1.8.2",
        "pyautogui>=0.9.53",
        "pystray>=0.19.4",
        "ttkthemes>=3.2.2",
        "psutil>=5.8.0",
        "memory_profiler>=0.60.0",
    ],
    entry_points={
        "console_scripts": [
            "mumble-notes=mumble_notes.app:main",
            "mumble-quick=mumble_quick.app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "mumble_notes": ["config/*.json", "assets/*"],
        "mumble_quick": ["config/*.json", "assets/*"],
    },
) 