"""
Launcher UI for Mumble applications
Provides a central interface to launch Mumble Notes and Mumble Quick
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import webbrowser
import time

class MumbleLauncher:
    """Launcher application for Mumble Notes and Mumble Quick"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Mumble Launcher")
        self.root.geometry("400x350")
        self.root.resizable(False, False)
        
        # Set icon if available
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.png")
        if os.path.exists(icon_path):
            icon = tk.PhotoImage(file=icon_path)
            self.root.iconphoto(True, icon)
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TButton", font=("Arial", 12))
        self.style.configure("TLabel", font=("Arial", 12), background="#f0f0f0")
        self.style.configure("Header.TLabel", font=("Arial", 16, "bold"), background="#f0f0f0")
        self.style.configure("Warning.TLabel", font=("Arial", 10), background="#f0f0f0", foreground="#CC0000")
        
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_label = ttk.Label(
            self.main_frame, 
            text="Mumble Application Launcher", 
            style="Header.TLabel"
        )
        header_label.pack(pady=(0, 20))
        
        # Exclusive mode warning
        exclusive_label = ttk.Label(
            self.main_frame,
            text="Only one application can run at a time",
            style="Warning.TLabel"
        )
        exclusive_label.pack(pady=(0, 10))
        
        # Mumble Notes button
        self.notes_button = ttk.Button(
            self.main_frame,
            text="Launch Mumble Notes",
            command=self.launch_notes,
            width=30
        )
        self.notes_button.pack(pady=10)
        
        # Mumble Quick button
        self.quick_button = ttk.Button(
            self.main_frame,
            text="Launch Mumble Quick",
            command=self.launch_quick,
            width=30
        )
        self.quick_button.pack(pady=10)
        
        # Status indicators
        self.notes_status = ttk.Label(
            self.main_frame,
            text="Mumble Notes: Not running",
            foreground="gray"
        )
        self.notes_status.pack(pady=(20, 5))
        
        self.quick_status = ttk.Label(
            self.main_frame,
            text="Mumble Quick: Not running",
            foreground="gray"
        )
        self.quick_status.pack(pady=5)
        
        # Stop button
        self.stop_button = ttk.Button(
            self.main_frame,
            text="Stop All Applications",
            command=self.terminate_processes,
            width=30
        )
        self.stop_button.pack(pady=10)
        self.stop_button.state(['disabled'])
        
        # Footer with help link
        help_link = ttk.Label(
            self.main_frame,
            text="Help & Documentation",
            foreground="blue",
            cursor="hand2"
        )
        help_link.pack(side=tk.BOTTOM, pady=10)
        help_link.bind("<Button-1>", self.open_documentation)
        
        # Track running processes
        self.notes_process = None
        self.quick_process = None
        
        # Set up exit handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Set up periodic health check
        self.health_check()
    
    def launch_notes(self):
        """Launch Mumble Notes application"""
        # Check if Quick is running and stop it if needed
        if self.quick_process and self.quick_process.poll() is None:
            if not messagebox.askyesno("Stop Mumble Quick", 
                                      "Mumble Quick is currently running. Stop it and launch Mumble Notes?"):
                return
            self.terminate_quick()
            # Wait a moment for the process to fully terminate
            time.sleep(0.5)
            
        if self.notes_process and self.notes_process.poll() is None:
            messagebox.showinfo("Already Running", "Mumble Notes is already running.")
            return
            
        try:
            # Get the path to the script
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                      "mumble_notes", "app.py")
            
            # Start the process without showing a console window
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0  # SW_HIDE
            
            # Set environment variable to help with dictation issues
            env = os.environ.copy()
            env["MUMBLE_DICTATION_TIMEOUT"] = "10"  # 10 second timeout for dictation
            
            self.notes_process = subprocess.Popen(
                [sys.executable, script_path],
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                env=env
            )
            
            # Update status and UI
            self.notes_status.config(text="Mumble Notes: Running", foreground="green")
            self.notes_button.state(['disabled'])
            self.stop_button.state(['!disabled'])
            
            # Start monitoring thread
            threading.Thread(target=self.monitor_notes_process, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Launch Error", f"Failed to launch Mumble Notes: {e}")
    
    def launch_quick(self):
        """Launch Mumble Quick application"""
        # Check if Notes is running and stop it if needed
        if self.notes_process and self.notes_process.poll() is None:
            if not messagebox.askyesno("Stop Mumble Notes", 
                                      "Mumble Notes is currently running. Stop it and launch Mumble Quick?"):
                return
            self.terminate_notes()
            # Wait a moment for the process to fully terminate
            time.sleep(0.5)
            
        if self.quick_process and self.quick_process.poll() is None:
            messagebox.showinfo("Already Running", "Mumble Quick is already running.")
            return
            
        try:
            # Get the path to the script
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                      "mumble_quick", "app.py")
            
            # Start the process without showing a console window
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0  # SW_HIDE
            
            # Set environment variable to help with dictation issues
            env = os.environ.copy()
            env["MUMBLE_DICTATION_TIMEOUT"] = "10"  # 10 second timeout for dictation
            
            self.quick_process = subprocess.Popen(
                [sys.executable, script_path],
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                env=env
            )
            
            # Update status and UI
            self.quick_status.config(text="Mumble Quick: Running", foreground="green")
            self.quick_button.state(['disabled'])
            self.stop_button.state(['!disabled'])
            
            # Start monitoring thread
            threading.Thread(target=self.monitor_quick_process, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Launch Error", f"Failed to launch Mumble Quick: {e}")
    
    def monitor_notes_process(self):
        """Monitor the Mumble Notes process and update status when it exits"""
        if self.notes_process:
            self.notes_process.wait()
            self.root.after(0, lambda: self.update_notes_status_stopped())
    
    def update_notes_status_stopped(self):
        """Update UI when Notes process has stopped"""
        self.notes_status.config(text="Mumble Notes: Not running", foreground="gray")
        self.notes_button.state(['!disabled'])
        if (not self.quick_process or self.quick_process.poll() is not None) and \
           (not self.notes_process or self.notes_process.poll() is not None):
            self.stop_button.state(['disabled'])
    
    def monitor_quick_process(self):
        """Monitor the Mumble Quick process and update status when it exits"""
        if self.quick_process:
            self.quick_process.wait()
            self.root.after(0, lambda: self.update_quick_status_stopped())
    
    def update_quick_status_stopped(self):
        """Update UI when Quick process has stopped"""
        self.quick_status.config(text="Mumble Quick: Not running", foreground="gray")
        self.quick_button.state(['!disabled'])
        if (not self.quick_process or self.quick_process.poll() is not None) and \
           (not self.notes_process or self.notes_process.poll() is not None):
            self.stop_button.state(['disabled'])
    
    def terminate_notes(self):
        """Terminate the Notes process"""
        if self.notes_process and self.notes_process.poll() is None:
            try:
                self.notes_process.terminate()
                # Give it a moment to terminate gracefully
                for _ in range(5):
                    if self.notes_process.poll() is not None:
                        break
                    time.sleep(0.1)
                # Force kill if still running
                if self.notes_process.poll() is None:
                    if sys.platform == "win32":
                        subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.notes_process.pid)])
                    else:
                        self.notes_process.kill()
            except Exception as e:
                print(f"Error terminating Notes: {e}")
            finally:
                self.update_notes_status_stopped()
    
    def terminate_quick(self):
        """Terminate the Quick process"""
        if self.quick_process and self.quick_process.poll() is None:
            try:
                self.quick_process.terminate()
                # Give it a moment to terminate gracefully
                for _ in range(5):
                    if self.quick_process.poll() is not None:
                        break
                    time.sleep(0.1)
                # Force kill if still running
                if self.quick_process.poll() is None:
                    if sys.platform == "win32":
                        subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.quick_process.pid)])
                    else:
                        self.quick_process.kill()
            except Exception as e:
                print(f"Error terminating Quick: {e}")
            finally:
                self.update_quick_status_stopped()
    
    def terminate_processes(self):
        """Terminate any running processes"""
        self.terminate_notes()
        self.terminate_quick()
    
    def health_check(self):
        """Periodically check the health of running processes"""
        # Check if processes have exited unexpectedly
        if self.notes_process and self.notes_process.poll() is not None:
            self.update_notes_status_stopped()
            
        if self.quick_process and self.quick_process.poll() is not None:
            self.update_quick_status_stopped()
            
        # Schedule next check
        self.root.after(1000, self.health_check)
    
    def open_documentation(self, event=None):
        """Open documentation in web browser"""
        # For now, just open the README file
        readme_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md")
        if os.path.exists(readme_path):
            webbrowser.open(f"file://{os.path.abspath(readme_path)}")
        else:
            messagebox.showinfo("Documentation", "Documentation not available.")
    
    def on_close(self):
        """Handle window close event"""
        # Check if any processes are running
        processes_running = False
        
        if self.notes_process and self.notes_process.poll() is None:
            processes_running = True
            
        if self.quick_process and self.quick_process.poll() is None:
            processes_running = True
            
        if processes_running:
            if messagebox.askyesno("Exit", "Applications are still running. Exit anyway?"):
                self.terminate_processes()
                self.root.destroy()
        else:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MumbleLauncher(root)
    root.mainloop() 