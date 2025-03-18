"""
Settings dialog for Mumble Quick
"""

import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from typing import Dict, Any, Callable
import logging

from ..config.quick_config import QuickConfig

logger = logging.getLogger('mumble.quick.settings')

class SettingsDialog(tk.Toplevel):
    """Settings dialog with tabbed interface"""
    
    def __init__(self, parent: tk.Widget, config: QuickConfig):
        """Initialize settings dialog"""
        super().__init__(parent)
        self.parent = parent
        self.config = config
        
        self.title("Mumble Quick Settings")
        self.geometry("500x400")
        self.resizable(True, True)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Initialize UI
        self._create_widgets()
        self._load_settings()
        
        # Center dialog
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def _create_widgets(self) -> None:
        """Create dialog widgets"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Create tabs
        self.hotkey_tab = self._create_hotkey_tab()
        self.ui_tab = self._create_ui_tab()
        self.speech_tab = self._create_speech_tab()
        self.tray_tab = self._create_tray_tab()
        self.behavior_tab = self._create_behavior_tab()
        
        # Add tabs to notebook
        self.notebook.add(self.hotkey_tab, text="Hotkeys")
        self.notebook.add(self.ui_tab, text="UI")
        self.notebook.add(self.speech_tab, text="Speech")
        self.notebook.add(self.tray_tab, text="System Tray")
        self.notebook.add(self.behavior_tab, text="Behavior")
        
        # Create bottom buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(button_frame, text="Apply", command=self._apply_settings).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Reset to Defaults", command=self._reset_defaults).pack(side='left', padx=5)
        
    def _create_hotkey_tab(self) -> ttk.Frame:
        """Create hotkey settings tab"""
        tab = ttk.Frame(self.notebook)
        tab.columnconfigure(1, weight=1)
        
        row = 0
        ttk.Label(tab, text="Trigger Hotkey:").grid(row=row, column=0, sticky='w', padx=5, pady=5)
        self.hotkey_trigger = ttk.Entry(tab)
        self.hotkey_trigger.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        
        row += 1
        ttk.Label(tab, text="Stop Hotkey:").grid(row=row, column=0, sticky='w', padx=5, pady=5)
        self.hotkey_stop = ttk.Entry(tab)
        self.hotkey_stop.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        
        return tab
        
    def _create_ui_tab(self) -> ttk.Frame:
        """Create UI settings tab"""
        tab = ttk.Frame(self.notebook)
        tab.columnconfigure(1, weight=1)
        
        row = 0
        ttk.Label(tab, text="Bar Width:").grid(row=row, column=0, sticky='w', padx=5, pady=5)
        self.bar_width = ttk.Spinbox(tab, from_=60, to=500)
        self.bar_width.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        
        row += 1
        ttk.Label(tab, text="Bar Height:").grid(row=row, column=0, sticky='w', padx=5, pady=5)
        self.bar_height = ttk.Spinbox(tab, from_=10, to=100)
        self.bar_height.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        
        # Color pickers
        row += 1
        ttk.Label(tab, text="Background Color:").grid(row=row, column=0, sticky='w', padx=5, pady=5)
        self.bg_color_frame = ttk.Frame(tab)
        self.bg_color_frame.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        self.bg_color = tk.StringVar()
        ttk.Entry(self.bg_color_frame, textvariable=self.bg_color).pack(side='left', expand=True, fill='x')
        ttk.Button(self.bg_color_frame, text="Pick", command=lambda: self._pick_color(self.bg_color)).pack(side='right', padx=5)
        
        row += 1
        ttk.Label(tab, text="Foreground Color:").grid(row=row, column=0, sticky='w', padx=5, pady=5)
        self.fg_color_frame = ttk.Frame(tab)
        self.fg_color_frame.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        self.fg_color = tk.StringVar()
        ttk.Entry(self.fg_color_frame, textvariable=self.fg_color).pack(side='left', expand=True, fill='x')
        ttk.Button(self.fg_color_frame, text="Pick", command=lambda: self._pick_color(self.fg_color)).pack(side='right', padx=5)
        
        row += 1
        ttk.Label(tab, text="Font Color:").grid(row=row, column=0, sticky='w', padx=5, pady=5)
        self.font_color_frame = ttk.Frame(tab)
        self.font_color_frame.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        self.font_color = tk.StringVar()
        ttk.Entry(self.font_color_frame, textvariable=self.font_color).pack(side='left', expand=True, fill='x')
        ttk.Button(self.font_color_frame, text="Pick", command=lambda: self._pick_color(self.font_color)).pack(side='right', padx=5)
        
        row += 1
        ttk.Label(tab, text="Opacity:").grid(row=row, column=0, sticky='w', padx=5, pady=5)
        self.opacity = ttk.Scale(tab, from_=0.1, to=1.0, orient='horizontal')
        self.opacity.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        
        row += 1
        ttk.Label(tab, text="Animation Speed:").grid(row=row, column=0, sticky='w', padx=5, pady=5)
        self.animation_speed = ttk.Scale(tab, from_=0.1, to=1.0, orient='horizontal')
        self.animation_speed.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        
        row += 1
        self.show_close_button = tk.BooleanVar()
        ttk.Checkbutton(tab, text="Show Close Button", variable=self.show_close_button).grid(row=row, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        
        return tab
        
    def _create_speech_tab(self) -> ttk.Frame:
        """Create speech settings tab"""
        tab = ttk.Frame(self.notebook)
        tab.columnconfigure(1, weight=1)
        
        row = 0
        ttk.Label(tab, text="Language:").grid(row=row, column=0, sticky='w', padx=5, pady=5)
        self.language = ttk.Combobox(tab, values=['en-US', 'en-GB', 'es-ES', 'fr-FR', 'de-DE'])
        self.language.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        
        row += 1
        ttk.Label(tab, text="Ambient Duration (seconds):").grid(row=row, column=0, sticky='w', padx=5, pady=5)
        self.ambient_duration = ttk.Spinbox(tab, from_=0.1, to=2.0, increment=0.1)
        self.ambient_duration.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        
        row += 1
        ttk.Label(tab, text="Phrase Timeout (seconds):").grid(row=row, column=0, sticky='w', padx=5, pady=5)
        self.phrase_timeout = ttk.Spinbox(tab, from_=0.0, to=10.0, increment=0.5)
        self.phrase_timeout.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        
        row += 1
        self.auto_stop = tk.BooleanVar()
        ttk.Checkbutton(tab, text="Auto Stop", variable=self.auto_stop).grid(row=row, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        
        row += 1
        ttk.Label(tab, text="Auto Stop Timeout (seconds):").grid(row=row, column=0, sticky='w', padx=5, pady=5)
        self.auto_stop_timeout = ttk.Spinbox(tab, from_=0.5, to=10.0, increment=0.5)
        self.auto_stop_timeout.grid(row=row, column=1, sticky='ew', padx=5, pady=5)
        
        return tab
        
    def _create_tray_tab(self) -> ttk.Frame:
        """Create system tray settings tab"""
        tab = ttk.Frame(self.notebook)
        tab.columnconfigure(1, weight=1)
        
        row = 0
        self.show_notifications = tk.BooleanVar()
        ttk.Checkbutton(tab, text="Show Notifications", variable=self.show_notifications).grid(row=row, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        
        row += 1
        self.minimize_to_tray = tk.BooleanVar()
        ttk.Checkbutton(tab, text="Minimize to Tray", variable=self.minimize_to_tray).grid(row=row, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        
        row += 1
        self.start_minimized = tk.BooleanVar()
        ttk.Checkbutton(tab, text="Start Minimized", variable=self.start_minimized).grid(row=row, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        
        return tab
        
    def _create_behavior_tab(self) -> ttk.Frame:
        """Create behavior settings tab"""
        tab = ttk.Frame(self.notebook)
        tab.columnconfigure(1, weight=1)
        
        row = 0
        self.auto_paste = tk.BooleanVar()
        ttk.Checkbutton(tab, text="Auto Paste", variable=self.auto_paste).grid(row=row, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        
        row += 1
        self.add_trailing_space = tk.BooleanVar()
        ttk.Checkbutton(tab, text="Add Trailing Space", variable=self.add_trailing_space).grid(row=row, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        
        row += 1
        self.capitalize_sentences = tk.BooleanVar()
        ttk.Checkbutton(tab, text="Capitalize Sentences", variable=self.capitalize_sentences).grid(row=row, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        
        row += 1
        self.save_position = tk.BooleanVar()
        ttk.Checkbutton(tab, text="Save Window Position", variable=self.save_position).grid(row=row, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        
        return tab
        
    def _load_settings(self) -> None:
        """Load current settings into UI"""
        # Hotkey settings
        hotkey = self.config.handler.get('hotkey')
        self.hotkey_trigger.insert(0, hotkey['trigger'])
        self.hotkey_stop.insert(0, hotkey['stop'])
        
        # UI settings
        ui = self.config.ui_settings
        self.bar_width.set(ui['bar_width'])
        self.bar_height.set(ui['bar_height'])
        self.bg_color.set(ui['background_color'])
        self.fg_color.set(ui['foreground_color'])
        self.font_color.set(ui['font_color'])
        self.opacity.set(ui['opacity'])
        self.animation_speed.set(ui['animation_speed'])
        self.show_close_button.set(ui['show_close_button'])
        
        # Speech settings
        speech = self.config.speech_settings
        self.language.set(speech['language'])
        self.ambient_duration.set(speech['ambient_duration'])
        self.phrase_timeout.set(speech['phrase_timeout'] or '')
        self.auto_stop.set(speech['auto_stop'])
        self.auto_stop_timeout.set(speech['auto_stop_timeout'])
        
        # Tray settings
        tray = self.config.tray_settings
        self.show_notifications.set(tray['show_notifications'])
        self.minimize_to_tray.set(tray['minimize_to_tray'])
        self.start_minimized.set(tray['start_minimized'])
        
        # Behavior settings
        behavior = self.config.behavior_settings
        self.auto_paste.set(behavior['auto_paste'])
        self.add_trailing_space.set(behavior['add_trailing_space'])
        self.capitalize_sentences.set(behavior['capitalize_sentences'])
        self.save_position.set(behavior['save_position'])
        
    def _apply_settings(self) -> None:
        """Apply settings from UI to config"""
        try:
            # Hotkey settings
            self.config.handler.set('hotkey', {
                'trigger': self.hotkey_trigger.get(),
                'stop': self.hotkey_stop.get()
            })
            
            # UI settings
            self.config.update_ui_settings({
                'bar_width': int(self.bar_width.get()),
                'bar_height': int(self.bar_height.get()),
                'background_color': self.bg_color.get(),
                'foreground_color': self.fg_color.get(),
                'font_color': self.font_color.get(),
                'opacity': float(self.opacity.get()),
                'animation_speed': float(self.animation_speed.get()),
                'show_close_button': self.show_close_button.get()
            })
            
            # Speech settings
            phrase_timeout = self.phrase_timeout.get()
            self.config.update_speech_settings({
                'language': self.language.get(),
                'ambient_duration': float(self.ambient_duration.get()),
                'phrase_timeout': float(phrase_timeout) if phrase_timeout else None,
                'auto_stop': self.auto_stop.get(),
                'auto_stop_timeout': float(self.auto_stop_timeout.get())
            })
            
            # Tray settings
            self.config.update_tray_settings({
                'show_notifications': self.show_notifications.get(),
                'minimize_to_tray': self.minimize_to_tray.get(),
                'start_minimized': self.start_minimized.get()
            })
            
            # Behavior settings
            self.config.update_behavior_settings({
                'auto_paste': self.auto_paste.get(),
                'add_trailing_space': self.add_trailing_space.get(),
                'capitalize_sentences': self.capitalize_sentences.get(),
                'save_position': self.save_position.get(),
                'last_position': self.config.behavior_settings['last_position']
            })
            
            logger.info("Settings applied successfully")
            self.destroy()
            
        except Exception as e:
            logger.error(f"Error applying settings: {e}")
            messagebox.showerror("Error", f"Failed to apply settings: {str(e)}")
            
    def _reset_defaults(self) -> None:
        """Reset all settings to defaults"""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            self.config.reset_to_defaults()
            self._load_settings()
            logger.info("Settings reset to defaults")
            
    def _pick_color(self, color_var: tk.StringVar) -> None:
        """Open color picker dialog"""
        color = colorchooser.askcolor(color_var.get())
        if color[1]:
            color_var.set(color[1]) 