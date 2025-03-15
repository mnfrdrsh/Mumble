#!/usr/bin/env python3
"""
Mumble - A simple speech-to-text application
"""

import os
import sys
import time
import threading
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, ttk
import speech_recognition as sr
from datetime import datetime


class MumbleApp:
    """Main application class for Mumble speech-to-text converter"""
    
    def __init__(self, root):
        """Initialize the application UI and components"""
        self.root = root
        self.root.title("Mumble - Speech to Text")
        self.root.geometry("900x600")  # Increased width for two-column layout
        self.root.minsize(800, 500)
        
        # Set up the recognizer
        self.recognizer = sr.Recognizer()
        
        # Initialize state variables
        self.is_recording = False
        self.transcription_thread = None
        self.should_stop = threading.Event()
        
        # Initialize temporary page storage
        self.pages = []
        self.current_page_index = -1  # No page selected initially
        
        # Create UI elements
        self._create_ui()
        
    def _create_ui(self):
        """Create the user interface elements"""
        # Main frame
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title label
        title_label = tk.Label(
            main_frame, 
            text="Mumble Speech-to-Text", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Create a PanedWindow for the two-column layout
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Left column - Text area frame
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=2)  # Give more weight to the text area
        
        # Text area for transcription
        text_frame = ttk.LabelFrame(left_frame, text="Current Transcription")
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5)
        
        self.text_area = scrolledtext.ScrolledText(
            text_frame, 
            wrap=tk.WORD, 
            font=("Arial", 12)
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        
        # Button frame
        button_frame = tk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Start/Stop button
        self.toggle_button = tk.Button(
            button_frame, 
            text="Start Recording", 
            command=self.toggle_recording,
            bg="#4CAF50", 
            fg="white", 
            font=("Arial", 12),
            padx=10, 
            pady=5
        )
        self.toggle_button.pack(side=tk.LEFT, padx=5)
        
        # Save button
        self.save_button = tk.Button(
            button_frame, 
            text="Save Text", 
            command=self.save_text,
            bg="#2196F3", 
            fg="white", 
            font=("Arial", 12),
            padx=10, 
            pady=5
        )
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        self.clear_button = tk.Button(
            button_frame, 
            text="Clear Text", 
            command=self.clear_text,
            bg="#f44336", 
            fg="white", 
            font=("Arial", 12),
            padx=10, 
            pady=5
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # New Page button
        self.new_page_button = tk.Button(
            button_frame, 
            text="New Page", 
            command=self.new_page,
            bg="#FF9800", 
            fg="white", 
            font=("Arial", 12),
            padx=10, 
            pady=5
        )
        self.new_page_button.pack(side=tk.LEFT, padx=5)
        
        # Right column - Pages list frame
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=1)
        
        # Pages list
        pages_frame = ttk.LabelFrame(right_frame, text="Saved Pages")
        pages_frame.pack(fill=tk.BOTH, expand=True, padx=5)
        
        # Create a frame for the listbox and scrollbar
        list_frame = ttk.Frame(pages_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar for the listbox
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox for pages
        self.pages_listbox = tk.Listbox(
            list_frame,
            font=("Arial", 11),
            selectmode=tk.SINGLE,
            yscrollcommand=scrollbar.set
        )
        self.pages_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.pages_listbox.yview)
        
        # Bind selection event
        self.pages_listbox.bind('<<ListboxSelect>>', self.on_page_select)
        
        # Pages buttons frame
        pages_button_frame = ttk.Frame(pages_frame)
        pages_button_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Delete page button
        self.delete_page_button = ttk.Button(
            pages_button_frame,
            text="Delete Page",
            command=self.delete_page
        )
        self.delete_page_button.pack(side=tk.LEFT, padx=5)
        
        # Save page to file button
        self.save_page_button = ttk.Button(
            pages_button_frame,
            text="Save Page to File",
            command=self.save_page_to_file
        )
        self.save_page_button.pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = tk.Label(
            main_frame, 
            textvariable=self.status_var, 
            bd=1, 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
    
    def toggle_recording(self):
        """Toggle between starting and stopping recording"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Start the speech recognition process"""
        self.is_recording = True
        self.should_stop.clear()
        self.toggle_button.config(text="Stop Recording", bg="#f44336")
        self.status_var.set("Listening...")
        
        # Start transcription in a separate thread
        self.transcription_thread = threading.Thread(target=self.transcribe_audio)
        self.transcription_thread.daemon = True
        self.transcription_thread.start()
    
    def stop_recording(self):
        """Stop the speech recognition process"""
        if self.is_recording:
            self.is_recording = False
            self.should_stop.set()
            self.toggle_button.config(text="Start Recording", bg="#4CAF50")
            self.status_var.set("Stopped")
    
    def transcribe_audio(self):
        """Continuously transcribe audio from the microphone"""
        try:
            with sr.Microphone() as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                while not self.should_stop.is_set():
                    try:
                        self.status_var.set("Listening...")
                        audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=5)
                        self.status_var.set("Processing...")
                        
                        # Use Google's speech recognition
                        text = self.recognizer.recognize_google(audio)
                        
                        # Update the text area
                        self.root.after(0, self.update_text_area, text)
                        
                    except sr.WaitTimeoutError:
                        continue
                    except sr.UnknownValueError:
                        self.status_var.set("Could not understand audio")
                        time.sleep(1)
                    except sr.RequestError as e:
                        self.root.after(0, self.show_error, f"Error with the speech recognition service: {e}")
                        break
        except Exception as e:
            self.root.after(0, self.show_error, f"Error initializing microphone: {e}")
    
    def update_text_area(self, text):
        """Update the text area with transcribed text"""
        current_text = self.text_area.get("1.0", tk.END).strip()
        if current_text:
            self.text_area.insert(tk.END, f" {text}")
        else:
            self.text_area.insert(tk.END, text)
        self.text_area.see(tk.END)  # Scroll to the end
        self.status_var.set("Ready")
    
    def save_text(self):
        """Save the current text as a new page"""
        text = self.text_area.get("1.0", tk.END).strip()
        if not text:
            messagebox.showinfo("Info", "There is no text to save.")
            return
        
        # Create a timestamp for the page
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create a preview (first 30 characters)
        preview = text[:30] + "..." if len(text) > 30 else text
        
        # Add to pages list
        self.pages.append({
            "timestamp": timestamp,
            "preview": preview,
            "content": text
        })
        
        # Update the listbox
        self.update_pages_listbox()
        
        # Show confirmation
        self.status_var.set(f"Page saved at {timestamp}")
    
    def update_pages_listbox(self):
        """Update the pages listbox with current pages"""
        self.pages_listbox.delete(0, tk.END)
        for page in self.pages:
            self.pages_listbox.insert(tk.END, f"{page['timestamp']} - {page['preview']}")
    
    def on_page_select(self, event):
        """Handle page selection from the listbox"""
        selection = self.pages_listbox.curselection()
        if selection:
            self.current_page_index = selection[0]
            # Load the selected page content into the text area
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, self.pages[self.current_page_index]["content"])
    
    def new_page(self):
        """Create a new empty page"""
        # Save current text if not empty
        current_text = self.text_area.get("1.0", tk.END).strip()
        if current_text:
            save_current = messagebox.askyesno(
                "Save Current Page", 
                "Do you want to save the current text as a page before creating a new one?"
            )
            if save_current:
                self.save_text()
        
        # Clear the text area for a new page
        self.text_area.delete("1.0", tk.END)
        self.current_page_index = -1  # No page selected
        self.status_var.set("New page created")
    
    def delete_page(self):
        """Delete the selected page"""
        if self.current_page_index >= 0:
            confirm = messagebox.askyesno(
                "Confirm Delete", 
                "Are you sure you want to delete this page?"
            )
            if confirm:
                del self.pages[self.current_page_index]
                self.update_pages_listbox()
                self.current_page_index = -1
                self.text_area.delete("1.0", tk.END)
                self.status_var.set("Page deleted")
        else:
            messagebox.showinfo("Info", "No page selected to delete.")
    
    def save_page_to_file(self):
        """Save the selected page to a file"""
        if self.current_page_index >= 0:
            page = self.pages[self.current_page_index]
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=f"Mumble_{page['timestamp'].replace(':', '-').replace(' ', '_')}.txt"
            )
            
            if file_path:
                try:
                    with open(file_path, "w", encoding="utf-8") as file:
                        file.write(page["content"])
                    messagebox.showinfo("Success", f"Page saved to {file_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save file: {e}")
        else:
            messagebox.showinfo("Info", "No page selected to save.")
    
    def clear_text(self):
        """Clear the text area"""
        confirm = messagebox.askyesno(
            "Confirm Clear", 
            "Are you sure you want to clear the current text?"
        )
        if confirm:
            self.text_area.delete("1.0", tk.END)
            if self.current_page_index >= 0:
                self.current_page_index = -1  # Deselect the current page
    
    def show_error(self, message):
        """Display an error message"""
        messagebox.showerror("Error", message)
        self.stop_recording()


def main():
    """Main entry point for the application"""
    root = tk.Tk()
    app = MumbleApp(root)
    # When closing the window, all temporary pages will be lost
    root.protocol("WM_DELETE_WINDOW", lambda: (app.stop_recording(), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    main() 