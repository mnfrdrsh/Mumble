"""
Debug script for Mumble Quick waveform bar visibility issues
"""

import sys
import os
import tkinter as tk
import time
import logging

# Add the source directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from mumble_quick.ui.pill_bar import WaveformBar


def test_basic_tkinter():
    """Test basic Tkinter window visibility"""
    print("=== Testing Basic Tkinter Window ===")
    
    root = tk.Tk()
    root.title("Tkinter Test")
    root.geometry("200x100+100+100")
    root.configure(bg='red')
    
    label = tk.Label(root, text="Can you see this red window?", bg='red', fg='white')
    label.pack(expand=True)
    
    print("Basic Tkinter window created. Should be visible now.")
    print("Close the window to continue...")
    
    root.mainloop()
    print("Basic Tkinter test completed.")


def test_frameless_window():
    """Test frameless window like the waveform bar"""
    print("\n=== Testing Frameless Window ===")
    
    root = tk.Tk()
    root.overrideredirect(True)  # Remove decorations
    root.geometry("200x50+200+200")
    root.configure(bg='blue')
    root.attributes('-topmost', True)
    
    label = tk.Label(root, text="Frameless blue window", bg='blue', fg='white')
    label.pack(expand=True)
    
    # Close button
    def close_window():
        root.destroy()
    
    close_btn = tk.Button(root, text="X", command=close_window, bg='red', fg='white')
    close_btn.place(x=175, y=5, width=20, height=20)
    
    print("Frameless window created. Should be visible now.")
    print("Click the X to close...")
    
    root.mainloop()
    print("Frameless window test completed.")


def test_waveform_bar():
    """Test the actual waveform bar"""
    print("\n=== Testing Waveform Bar ===")
    
    # Set up logging to see what's happening
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    try:
        print("Creating WaveformBar...")
        bar = WaveformBar()
        
        print("WaveformBar created successfully.")
        print("Calling show() method...")
        
        # Show the bar
        bar.show()
        
        print("Show() method called.")
        print("Checking window state...")
        
        # Check window properties
        try:
            print(f"Window geometry: {bar.geometry()}")
            print(f"Window position: ({bar.winfo_x()}, {bar.winfo_y()})")
            print(f"Window size: {bar.winfo_width()}x{bar.winfo_height()}")
            print(f"Window viewable: {bar.winfo_viewable()}")
            print(f"Window mapped: {bar.winfo_ismapped()}")
        except Exception as e:
            print(f"Error checking window properties: {e}")
        
        print("\nThe waveform bar should be visible now.")
        print("Look for a small dark pill-shaped window with green animation.")
        print("It should be at the bottom center of your screen.")
        print("Press Ctrl+C to exit...")
        
        try:
            bar.mainloop()
        except KeyboardInterrupt:
            print("\nInterrupted by user.")
        
    except Exception as e:
        print(f"Error creating/showing WaveformBar: {e}")
        import traceback
        traceback.print_exc()
    
    print("Waveform bar test completed.")


def main():
    """Run all diagnostic tests"""
    print("Mumble Quick Waveform Bar Diagnostic Tool")
    print("=" * 50)
    
    while True:
        print("\nChoose a test:")
        print("1. Basic Tkinter window test")
        print("2. Frameless window test") 
        print("3. Waveform bar test")
        print("4. Run all tests")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            test_basic_tkinter()
        elif choice == "2":
            test_frameless_window()
        elif choice == "3":
            test_waveform_bar()
        elif choice == "4":
            test_basic_tkinter()
            test_frameless_window()
            test_waveform_bar()
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter 1-5.")


if __name__ == "__main__":
    main() 