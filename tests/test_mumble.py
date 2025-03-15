#!/usr/bin/env python3
"""
Tests for the Mumble application
"""

import unittest
import sys
import os

# Add the src directory to the path so we can import the main module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import the main module
import main


class TestMumble(unittest.TestCase):
    """Test cases for the Mumble application"""
    
    def test_app_initialization(self):
        """Test that the application class can be initialized"""
        # This is a simple test to ensure the module can be imported
        self.assertTrue(hasattr(main, 'MumbleApp'), "MumbleApp class should exist")
        self.assertTrue(hasattr(main, 'main'), "main function should exist")
    
    # Add more tests as the application develops


if __name__ == '__main__':
    unittest.main() 