#!/usr/bin/env python3
"""
Modern Mumble UI Demo Launcher
Launch the demo showcasing the redesigned UI components
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == '__main__':
    try:
        from ui_redesign.demo import main
        main()
    except ImportError as e:
        print(f"Error importing demo: {e}")
        print("Make sure PyQt5 is installed: pip install PyQt5")
        sys.exit(1)
    except Exception as e:
        print(f"Error running demo: {e}")
        sys.exit(1) 