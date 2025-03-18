#!/usr/bin/env python3
"""
Create Windows shortcuts for Mumble applications
"""

import os
import sys
import winshell
from win32com.client import Dispatch

def create_shortcut(target_path, shortcut_name, description, icon_path=None):
    """Create a Windows shortcut"""
    desktop = winshell.desktop()
    shortcut_path = os.path.join(desktop, f"{shortcut_name}.lnk")
    
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = sys.executable
    shortcut.Arguments = f'"{target_path}"'
    shortcut.WorkingDirectory = os.path.dirname(target_path)
    shortcut.Description = description
    if icon_path:
        shortcut.IconLocation = icon_path
    shortcut.save()
    
    return shortcut_path

def main():
    """Create shortcuts for both applications"""
    try:
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Create Mumble Notes shortcut
        notes_path = os.path.join(script_dir, "run_notes.py")
        notes_icon = os.path.join(script_dir, "src", "assets", "notes_icon.ico")
        if os.path.exists(notes_path):
            notes_shortcut = create_shortcut(
                notes_path,
                "Mumble Notes",
                "Launch Mumble Notes - Rich Text Editor with Speech Recognition",
                notes_icon if os.path.exists(notes_icon) else None
            )
            print(f"Created Mumble Notes shortcut: {notes_shortcut}")
        
        # Create Mumble Quick shortcut
        quick_path = os.path.join(script_dir, "run_quick.py")
        quick_icon = os.path.join(script_dir, "src", "assets", "quick_icon.ico")
        if os.path.exists(quick_path):
            quick_shortcut = create_shortcut(
                quick_path,
                "Mumble Quick",
                "Launch Mumble Quick - Quick Speech-to-Text Tool",
                quick_icon if os.path.exists(quick_icon) else None
            )
            print(f"Created Mumble Quick shortcut: {quick_shortcut}")
        
        print("\nShortcuts created successfully!")
        print("You can find them on your desktop.")
        
    except Exception as e:
        print(f"Error creating shortcuts: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if sys.platform != 'win32':
        print("This script is for Windows only.")
        sys.exit(1)
    main() 