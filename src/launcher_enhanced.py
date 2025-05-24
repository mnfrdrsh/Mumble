"""
Enhanced Launcher UI for Mumble applications using modern Tkinter
Modern styling and improved UX while maintaining compatibility
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import webbrowser
import time


class ModernStyle:
    """Modern color scheme and styling constants"""
    
    # Color palette
    COLORS = {
        'bg_primary': '#f8f9fa',
        'bg_secondary': '#e9ecef',
        'bg_dark': '#343a40',
        'accent_blue': '#007bff',
        'accent_blue_hover': '#0056b3',
        'accent_green': '#28a745',
        'accent_red': '#dc3545',
        'accent_orange': '#fd7e14',
        'text_primary': '#212529',
        'text_secondary': '#6c757d',
        'text_light': '#ffffff',
        'border': '#dee2e6',
        'shadow': '#00000020'
    }
    
    # Fonts
    FONTS = {
        'header': ('Segoe UI', 16, 'bold'),
        'subheader': ('Segoe UI', 12, 'bold'),
        'body': ('Segoe UI', 10),
        'button': ('Segoe UI', 11, 'bold'),
        'small': ('Segoe UI', 8)
    }


class ModernButton(tk.Button):
    """Custom button with modern styling and hover effects"""
    
    def __init__(self, parent, text, command=None, style='primary', **kwargs):
        self.style_type = style
        self.default_config = self._get_style_config(style)
        self.hover_config = self._get_hover_config(style)
        
        super().__init__(
            parent,
            text=text,
            command=command,
            font=ModernStyle.FONTS['button'],
            relief='flat',
            bd=0,
            cursor='hand2',
            **self.default_config,
            **kwargs
        )
        
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_click)
        self.bind('<ButtonRelease-1>', self._on_release)
    
    def _get_style_config(self, style):
        """Get default configuration for button style"""
        styles = {
            'primary': {
                'bg': ModernStyle.COLORS['accent_blue'],
                'fg': ModernStyle.COLORS['text_light'],
                'activebackground': ModernStyle.COLORS['accent_blue_hover'],
                'activeforeground': ModernStyle.COLORS['text_light']
            },
            'success': {
                'bg': ModernStyle.COLORS['accent_green'],
                'fg': ModernStyle.COLORS['text_light'],
                'activebackground': '#1e7e34',
                'activeforeground': ModernStyle.COLORS['text_light']
            },
            'danger': {
                'bg': ModernStyle.COLORS['accent_red'],
                'fg': ModernStyle.COLORS['text_light'],
                'activebackground': '#c82333',
                'activeforeground': ModernStyle.COLORS['text_light']
            },
            'secondary': {
                'bg': ModernStyle.COLORS['bg_secondary'],
                'fg': ModernStyle.COLORS['text_primary'],
                'activebackground': '#d1ecf1',
                'activeforeground': ModernStyle.COLORS['text_primary']
            }
        }
        return styles.get(style, styles['primary'])
    
    def _get_hover_config(self, style):
        """Get hover configuration for button style"""
        hovers = {
            'primary': {'bg': ModernStyle.COLORS['accent_blue_hover']},
            'success': {'bg': '#1e7e34'},
            'danger': {'bg': '#c82333'},
            'secondary': {'bg': '#d1ecf1'}
        }
        return hovers.get(style, hovers['primary'])
    
    def _on_enter(self, event):
        """Handle mouse enter"""
        self.configure(**self.hover_config)
    
    def _on_leave(self, event):
        """Handle mouse leave"""
        self.configure(**self.default_config)
    
    def _on_click(self, event):
        """Handle mouse click"""
        # Add slight color change on click
        click_config = self.hover_config.copy()
        if 'bg' in click_config:
            # Darken the color slightly
            color = click_config['bg']
            if color.startswith('#'):
                rgb = int(color[1:], 16)
                r, g, b = (rgb >> 16) & 255, (rgb >> 8) & 255, rgb & 255
                r, g, b = max(0, r-20), max(0, g-20), max(0, b-20)
                click_config['bg'] = f'#{r:02x}{g:02x}{b:02x}'
        self.configure(**click_config)
    
    def _on_release(self, event):
        """Handle mouse release"""
        self._on_enter(event)  # Return to hover state


class StatusIndicator(tk.Frame):
    """Modern status indicator with colored dots"""
    
    def __init__(self, parent, text, **kwargs):
        super().__init__(parent, bg=ModernStyle.COLORS['bg_primary'], **kwargs)
        
        # Create status dot
        self.canvas = tk.Canvas(
            self,
            width=12,
            height=12,
            bg=ModernStyle.COLORS['bg_primary'],
            highlightthickness=0
        )
        self.canvas.pack(side=tk.LEFT, padx=(0, 8))
        
        self.dot = self.canvas.create_oval(
            2, 2, 10, 10,
            fill=ModernStyle.COLORS['text_secondary'],
            outline=''
        )
        
        # Create status text
        self.label = tk.Label(
            self,
            text=text,
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['bg_primary'],
            fg=ModernStyle.COLORS['text_secondary']
        )
        self.label.pack(side=tk.LEFT)
    
    def set_status(self, status, text):
        """Update status indicator"""
        colors = {
            'running': ModernStyle.COLORS['accent_green'],
            'stopped': ModernStyle.COLORS['text_secondary'],
            'error': ModernStyle.COLORS['accent_red']
        }
        
        self.canvas.itemconfig(self.dot, fill=colors.get(status, colors['stopped']))
        self.label.config(text=text)
        
        if status == 'running':
            self.label.config(fg=ModernStyle.COLORS['text_primary'])
        else:
            self.label.config(fg=ModernStyle.COLORS['text_secondary'])


class EnhancedMumbleLauncher:
    """Enhanced launcher application with modern UI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Mumble Launcher")
        self.root.geometry("500x600")
        self.root.resizable(False, False)
        self.root.configure(bg=ModernStyle.COLORS['bg_primary'])
        
        # Set window icon if available
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.png")
        if os.path.exists(icon_path):
            try:
                icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, icon)
            except:
                pass
        
        # Initialize UI
        self._create_ui()
        self._init_variables()
        
        # Set up exit handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Set up periodic health check
        self.health_check()
    
    def _create_ui(self):
        """Create the modern user interface"""
        # Main container with padding
        main_container = tk.Frame(
            self.root,
            bg=ModernStyle.COLORS['bg_primary'],
            padx=30,
            pady=30
        )
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header section
        self._create_header(main_container)
        
        # Warning section
        self._create_warning(main_container)
        
        # Applications section
        self._create_applications_section(main_container)
        
        # Status section
        self._create_status_section(main_container)
        
        # Information section
        self._create_info_section(main_container)
        
        # Control section
        self._create_control_section(main_container)
    
    def _create_header(self, parent):
        """Create header section"""
        header_frame = tk.Frame(parent, bg=ModernStyle.COLORS['bg_primary'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Main title
        title_label = tk.Label(
            header_frame,
            text="🎙️ Mumble Application Launcher",
            font=ModernStyle.FONTS['header'],
            bg=ModernStyle.COLORS['bg_primary'],
            fg=ModernStyle.COLORS['text_primary']
        )
        title_label.pack()
        
        # Subtitle
        subtitle_label = tk.Label(
            header_frame,
            text="Voice-powered productivity tools",
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['bg_primary'],
            fg=ModernStyle.COLORS['text_secondary']
        )
        subtitle_label.pack(pady=(5, 0))
    
    def _create_warning(self, parent):
        """Create warning section"""
        warning_frame = tk.Frame(
            parent,
            bg=ModernStyle.COLORS['accent_orange'],
            relief=tk.SOLID,
            bd=1
        )
        warning_frame.pack(fill=tk.X, pady=(0, 20), ipady=10)
        
        warning_label = tk.Label(
            warning_frame,
            text="⚠️ Only one application can run at a time",
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['accent_orange'],
            fg=ModernStyle.COLORS['text_light']
        )
        warning_label.pack()
    
    def _create_applications_section(self, parent):
        """Create applications section"""
        apps_frame = tk.LabelFrame(
            parent,
            text="Applications",
            font=ModernStyle.FONTS['subheader'],
            bg=ModernStyle.COLORS['bg_primary'],
            fg=ModernStyle.COLORS['text_primary'],
            relief=tk.SOLID,
            bd=1
        )
        apps_frame.pack(fill=tk.X, pady=(0, 20), padx=10, ipady=15)
        
        # Mumble Notes
        notes_container = tk.Frame(apps_frame, bg=ModernStyle.COLORS['bg_primary'])
        notes_container.pack(fill=tk.X, pady=(10, 15), padx=20)
        
        self.notes_button = ModernButton(
            notes_container,
            text="📝 Launch Mumble Notes",
            command=self.launch_notes,
            style='primary'
        )
        self.notes_button.pack(fill=tk.X, ipady=8)
        
        notes_desc = tk.Label(
            notes_container,
            text="Full-featured text editor with speech-to-text capabilities",
            font=ModernStyle.FONTS['small'],
            bg=ModernStyle.COLORS['bg_primary'],
            fg=ModernStyle.COLORS['text_secondary']
        )
        notes_desc.pack(pady=(5, 0))
        
        # Mumble Quick
        quick_container = tk.Frame(apps_frame, bg=ModernStyle.COLORS['bg_primary'])
        quick_container.pack(fill=tk.X, pady=(0, 10), padx=20)
        
        self.quick_button = ModernButton(
            quick_container,
            text="⚡ Launch Mumble Quick",
            command=self.launch_quick,
            style='success'
        )
        self.quick_button.pack(fill=tk.X, ipady=8)
        
        quick_desc = tk.Label(
            quick_container,
            text="Background voice input - Press Ctrl+Alt to dictate anywhere",
            font=ModernStyle.FONTS['small'],
            bg=ModernStyle.COLORS['bg_primary'],
            fg=ModernStyle.COLORS['text_secondary']
        )
        quick_desc.pack(pady=(5, 0))
    
    def _create_status_section(self, parent):
        """Create status section"""
        status_frame = tk.LabelFrame(
            parent,
            text="Status",
            font=ModernStyle.FONTS['subheader'],
            bg=ModernStyle.COLORS['bg_primary'],
            fg=ModernStyle.COLORS['text_primary'],
            relief=tk.SOLID,
            bd=1
        )
        status_frame.pack(fill=tk.X, pady=(0, 20), padx=10, ipady=15)
        
        status_container = tk.Frame(status_frame, bg=ModernStyle.COLORS['bg_primary'])
        status_container.pack(fill=tk.X, padx=20, pady=10)
        
        self.notes_status = StatusIndicator(
            status_container,
            "Mumble Notes: Not running"
        )
        self.notes_status.pack(fill=tk.X, pady=(0, 8))
        
        self.quick_status = StatusIndicator(
            status_container,
            "Mumble Quick: Not running"
        )
        self.quick_status.pack(fill=tk.X)
    
    def _create_info_section(self, parent):
        """Create information section"""
        info_frame = tk.LabelFrame(
            parent,
            text="Quick Tips",
            font=ModernStyle.FONTS['subheader'],
            bg=ModernStyle.COLORS['bg_primary'],
            fg=ModernStyle.COLORS['text_primary'],
            relief=tk.SOLID,
            bd=1
        )
        info_frame.pack(fill=tk.X, pady=(0, 20), padx=10, ipady=15)
        
        info_container = tk.Frame(info_frame, bg=ModernStyle.COLORS['bg_primary'])
        info_container.pack(fill=tk.X, padx=20, pady=10)
        
        tips = [
            "💡 Mumble Notes opens a dedicated editor window for longer text",
            "🎯 Mumble Quick runs in background - perfect for quick dictation",
            "⌨️ Use Ctrl+Alt hotkey to activate Mumble Quick from anywhere",
            "🔄 Switch between apps easily - the launcher handles the rest"
        ]
        
        for tip in tips:
            tip_label = tk.Label(
                info_container,
                text=tip,
                font=ModernStyle.FONTS['small'],
                bg=ModernStyle.COLORS['bg_primary'],
                fg=ModernStyle.COLORS['text_secondary'],
                anchor='w'
            )
            tip_label.pack(fill=tk.X, pady=2)
    
    def _create_control_section(self, parent):
        """Create control section"""
        control_frame = tk.Frame(parent, bg=ModernStyle.COLORS['bg_primary'])
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Stop button
        self.stop_button = ModernButton(
            control_frame,
            text="🛑 Stop All Applications",
            command=self.terminate_processes,
            style='danger'
        )
        self.stop_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=6)
        self.stop_button.configure(state='disabled')
        
        # Help button
        help_button = ModernButton(
            control_frame,
            text="❓ Help & Documentation",
            command=self.open_documentation,
            style='secondary'
        )
        help_button.pack(side=tk.RIGHT, padx=(10, 0), ipady=6)
    
    def _init_variables(self):
        """Initialize instance variables"""
        self.notes_process = None
        self.quick_process = None
    
    def launch_notes(self):
        """Launch Mumble Notes application"""
        # Check if Quick is running and stop it if needed
        if self.quick_process and self.quick_process.poll() is None:
            if not messagebox.askyesno(
                "Stop Mumble Quick", 
                "Mumble Quick is currently running. Stop it and launch Mumble Notes?",
                icon='question'
            ):
                return
            self.terminate_quick()
            time.sleep(0.5)
            
        if self.notes_process and self.notes_process.poll() is None:
            messagebox.showinfo("Already Running", "Mumble Notes is already running.", icon='info')
            return
            
        try:
            # Get the path to the script
            script_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 
                "mumble_notes", "app.py"
            )
            
            # Set environment variable
            env = os.environ.copy()
            env["MUMBLE_DICTATION_TIMEOUT"] = "10"
            
            # Start Mumble Notes
            self.notes_process = subprocess.Popen(
                [sys.executable, script_path],
                env=env
            )
            
            # Update UI
            self.notes_status.set_status("running", "Mumble Notes: Running")
            self.notes_button.configure(state='disabled')
            self.stop_button.configure(state='normal')
            
            # Start monitoring thread
            threading.Thread(target=self.monitor_notes_process, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Launch Error", f"Failed to launch Mumble Notes:\n{e}", icon='error')
    
    def launch_quick(self):
        """Launch Mumble Quick application"""
        # Check if Notes is running and stop it if needed
        if self.notes_process and self.notes_process.poll() is None:
            if not messagebox.askyesno(
                "Stop Mumble Notes", 
                "Mumble Notes is currently running. Stop it and launch Mumble Quick?",
                icon='question'
            ):
                return
            self.terminate_notes()
            time.sleep(0.5)
            
        if self.quick_process and self.quick_process.poll() is None:
            messagebox.showinfo("Already Running", "Mumble Quick is already running.", icon='info')
            return
            
        try:
            # Get the path to the script
            script_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 
                "mumble_quick", "app.py"
            )
            
            # Set environment variable
            env = os.environ.copy()
            env["MUMBLE_DICTATION_TIMEOUT"] = "10"
            
            # Start Mumble Quick
            if os.name == 'nt':  # Windows
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                self.quick_process = subprocess.Popen(
                    [sys.executable, script_path],
                    env=env,
                    startupinfo=startupinfo
                )
            else:
                self.quick_process = subprocess.Popen(
                    [sys.executable, script_path],
                    env=env
                )
            
            # Update UI
            self.quick_status.set_status("running", "Mumble Quick: Running")
            self.quick_button.configure(state='disabled')
            self.stop_button.configure(state='normal')
            
            # Start monitoring thread
            threading.Thread(target=self.monitor_quick_process, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Launch Error", f"Failed to launch Mumble Quick:\n{e}", icon='error')
    
    def monitor_notes_process(self):
        """Monitor Mumble Notes process"""
        if self.notes_process:
            self.notes_process.wait()
            self.root.after(0, self.update_notes_status_stopped)
    
    def update_notes_status_stopped(self):
        """Update UI when Notes process stops"""
        self.notes_status.set_status("stopped", "Mumble Notes: Not running")
        self.notes_button.configure(state='normal')
        self._check_stop_button_state()
    
    def monitor_quick_process(self):
        """Monitor Mumble Quick process"""
        if self.quick_process:
            self.quick_process.wait()
            self.root.after(0, self.update_quick_status_stopped)
    
    def update_quick_status_stopped(self):
        """Update UI when Quick process stops"""
        self.quick_status.set_status("stopped", "Mumble Quick: Not running")
        self.quick_button.configure(state='normal')
        self._check_stop_button_state()
    
    def _check_stop_button_state(self):
        """Check if stop button should be enabled"""
        any_running = False
        if self.notes_process and self.notes_process.poll() is None:
            any_running = True
        if self.quick_process and self.quick_process.poll() is None:
            any_running = True
        
        self.stop_button.configure(state='normal' if any_running else 'disabled')
    
    def terminate_notes(self):
        """Terminate Mumble Notes process"""
        try:
            if self.notes_process and self.notes_process.poll() is None:
                self.notes_process.terminate()
                try:
                    self.notes_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.notes_process.kill()
                self.update_notes_status_stopped()
        except Exception as e:
            print(f"Error terminating Mumble Notes: {e}")
    
    def terminate_quick(self):
        """Terminate Mumble Quick process"""
        try:
            if self.quick_process and self.quick_process.poll() is None:
                self.quick_process.terminate()
                try:
                    self.quick_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.quick_process.kill()
                self.update_quick_status_stopped()
        except Exception as e:
            print(f"Error terminating Mumble Quick: {e}")
    
    def terminate_processes(self):
        """Terminate all running processes"""
        self.terminate_notes()
        self.terminate_quick()
    
    def health_check(self):
        """Periodic health check for processes"""
        try:
            # Check notes process
            if self.notes_process and self.notes_process.poll() is not None:
                if "Running" in self.notes_status.label.cget("text"):
                    self.update_notes_status_stopped()
            
            # Check quick process
            if self.quick_process and self.quick_process.poll() is not None:
                if "Running" in self.quick_status.label.cget("text"):
                    self.update_quick_status_stopped()
        except Exception as e:
            print(f"Error in health check: {e}")
        
        # Schedule next check
        self.root.after(5000, self.health_check)
    
    def open_documentation(self):
        """Open documentation in browser"""
        try:
            webbrowser.open("https://github.com/yourusername/mumble")
        except Exception:
            messagebox.showinfo(
                "Help", 
                "Documentation: https://github.com/yourusername/mumble\n\n"
                "Mumble Notes: Full editor with speech-to-text\n"
                "Mumble Quick: Background voice input (Ctrl+Alt to activate)",
                icon='info'
            )
    
    def on_close(self):
        """Handle window close event"""
        self.terminate_processes()
        self.root.destroy()


def main():
    """Main function to run the enhanced launcher"""
    root = tk.Tk()
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_reqwidth()
    height = root.winfo_reqheight()
    pos_x = (root.winfo_screenwidth() // 2) - (width // 2)
    pos_y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
    
    app = EnhancedMumbleLauncher(root)
    root.mainloop()


if __name__ == '__main__':
    main() 