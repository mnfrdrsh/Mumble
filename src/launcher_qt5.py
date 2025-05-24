"""
PyQt5 Launcher UI for Mumble applications
Modern replacement for the Tkinter-based launcher
"""

import os
import sys
import subprocess
import threading
import webbrowser
import time
import logging
import traceback

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFrame, QMessageBox, QGroupBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPalette, QColor


class ProcessMonitorThread(QThread):
    """Thread to monitor subprocess status"""
    process_stopped = pyqtSignal(str)  # Emits process name when stopped
    
    def __init__(self, process, process_name):
        super().__init__()
        self.process = process
        self.process_name = process_name
        self.running = True
    
    def run(self):
        """Monitor the process"""
        try:
            while self.running and self.process:
                if self.process.poll() is not None:
                    # Process has terminated
                    self.process_stopped.emit(self.process_name)
                    break
                time.sleep(1)
        except Exception as e:
            print(f"Error in process monitor: {e}")
    
    def stop(self):
        """Stop monitoring"""
        self.running = False


class MumbleLauncher(QWidget):
    """Modern PyQt5 launcher for Mumble applications"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('mumble.launcher')
        self.init_ui()
        self.init_variables()
        
    def init_variables(self):
        """Initialize instance variables"""
        self.notes_process = None
        self.quick_process = None
        self.notes_monitor = None
        self.quick_monitor = None
        
        # Start health check timer
        self.health_timer = QTimer()
        self.health_timer.timeout.connect(self.health_check)
        self.health_timer.start(5000)  # Check every 5 seconds
    
    def init_ui(self):
        """Initialize the user interface"""
        try:
            self.setWindowTitle("Mumble Launcher")
            self.setFixedSize(450, 400)
            
            # Set application icon if available
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.png")
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
            
            # Apply modern styling
            self._apply_styling()
            
            # Create layout
            main_layout = QVBoxLayout()
            main_layout.setSpacing(20)
            main_layout.setContentsMargins(30, 30, 30, 30)
            
            # Header
            header_label = QLabel("Mumble Application Launcher")
            header_label.setObjectName("header")
            header_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(header_label)
            
            # Exclusive mode warning
            warning_frame = QFrame()
            warning_frame.setObjectName("warning")
            warning_layout = QHBoxLayout(warning_frame)
            warning_label = QLabel("⚠ Only one application can run at a time")
            warning_label.setObjectName("warning_text")
            warning_label.setAlignment(Qt.AlignCenter)
            warning_layout.addWidget(warning_label)
            main_layout.addWidget(warning_frame)
            
            # Application buttons group
            app_group = QGroupBox("Applications")
            app_group.setObjectName("app_group")
            app_layout = QVBoxLayout()
            app_layout.setSpacing(15)
            
            # Mumble Notes button
            self.notes_button = QPushButton("🗒 Launch Mumble Notes")
            self.notes_button.setObjectName("app_button")
            self.notes_button.clicked.connect(self.launch_notes)
            app_layout.addWidget(self.notes_button)
            
            # Mumble Quick button
            self.quick_button = QPushButton("⚡ Launch Mumble Quick")
            self.quick_button.setObjectName("app_button")
            self.quick_button.clicked.connect(self.launch_quick)
            app_layout.addWidget(self.quick_button)
            
            app_group.setLayout(app_layout)
            main_layout.addWidget(app_group)
            
            # Status group
            status_group = QGroupBox("Status")
            status_group.setObjectName("status_group")
            status_layout = QVBoxLayout()
            
            self.notes_status = QLabel("Mumble Notes: Not running")
            self.notes_status.setObjectName("status_label")
            status_layout.addWidget(self.notes_status)
            
            self.quick_status = QLabel("Mumble Quick: Not running")
            self.quick_status.setObjectName("status_label")
            status_layout.addWidget(self.quick_status)
            
            status_group.setLayout(status_layout)
            main_layout.addWidget(status_group)
            
            # Info group
            info_group = QGroupBox("Information")
            info_group.setObjectName("info_group")
            info_layout = QVBoxLayout()
            
            notes_info = QLabel("• Mumble Notes: Opens a full editor window")
            notes_info.setObjectName("info_label")
            info_layout.addWidget(notes_info)
            
            quick_info = QLabel("• Mumble Quick: Runs hidden, press Ctrl+Alt to use")
            quick_info.setObjectName("info_label")
            info_layout.addWidget(quick_info)
            
            info_group.setLayout(info_layout)
            main_layout.addWidget(info_group)
            
            # Control buttons
            control_layout = QHBoxLayout()
            
            self.stop_button = QPushButton("🛑 Stop All Applications")
            self.stop_button.setObjectName("stop_button")
            self.stop_button.clicked.connect(self.terminate_processes)
            self.stop_button.setEnabled(False)
            control_layout.addWidget(self.stop_button)
            
            help_button = QPushButton("❓ Help")
            help_button.setObjectName("help_button")
            help_button.clicked.connect(self.open_documentation)
            control_layout.addWidget(help_button)
            
            main_layout.addLayout(control_layout)
            
            self.setLayout(main_layout)
            
        except Exception as e:
            self.logger.error(f"Error initializing UI: {e}")
            self.logger.error(traceback.format_exc())
    
    def _apply_styling(self):
        """Apply modern CSS-like styling to the application"""
        style = """
        QWidget {
            background-color: #f5f5f5;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        
        QLabel#header {
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
        }
        
        QFrame#warning {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 10px;
        }
        
        QLabel#warning_text {
            color: #856404;
            font-weight: bold;
        }
        
        QGroupBox {
            font-weight: bold;
            font-size: 12px;
            color: #2c3e50;
            margin-top: 10px;
            padding-top: 10px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        
        QPushButton#app_button {
            background-color: #3498db;
            border: none;
            color: white;
            padding: 12px;
            text-align: center;
            text-decoration: none;
            font-size: 14px;
            font-weight: bold;
            margin: 2px;
            border-radius: 6px;
        }
        
        QPushButton#app_button:hover {
            background-color: #2980b9;
        }
        
        QPushButton#app_button:pressed {
            background-color: #21618c;
        }
        
        QPushButton#app_button:disabled {
            background-color: #bdc3c7;
            color: #7f8c8d;
        }
        
        QPushButton#stop_button {
            background-color: #e74c3c;
            border: none;
            color: white;
            padding: 10px;
            text-align: center;
            font-size: 12px;
            font-weight: bold;
            margin: 2px;
            border-radius: 6px;
        }
        
        QPushButton#stop_button:hover {
            background-color: #c0392b;
        }
        
        QPushButton#stop_button:disabled {
            background-color: #bdc3c7;
            color: #7f8c8d;
        }
        
        QPushButton#help_button {
            background-color: #95a5a6;
            border: none;
            color: white;
            padding: 10px;
            text-align: center;
            font-size: 12px;
            font-weight: bold;
            margin: 2px;
            border-radius: 6px;
        }
        
        QPushButton#help_button:hover {
            background-color: #7f8c8d;
        }
        
        QLabel#status_label {
            color: #7f8c8d;
            font-size: 11px;
            padding: 2px;
        }
        
        QLabel#info_label {
            color: #34495e;
            font-size: 10px;
            padding: 2px;
        }
        """
        self.setStyleSheet(style)
    
    def launch_notes(self):
        """Launch Mumble Notes application"""
        try:
            # Check if Quick is running and stop it if needed
            if self.quick_process and self.quick_process.poll() is None:
                reply = QMessageBox.question(
                    self, 'Stop Mumble Quick', 
                    'Mumble Quick is currently running. Stop it and launch Mumble Notes?',
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return
                self.terminate_quick()
                time.sleep(0.5)
            
            if self.notes_process and self.notes_process.poll() is None:
                QMessageBox.information(self, "Already Running", "Mumble Notes is already running.")
                return
            
            # Get the path to the script
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                      "mumble_notes", "app.py")
            
            # Set environment variable to help with dictation issues
            env = os.environ.copy()
            env["MUMBLE_DICTATION_TIMEOUT"] = "10"
            
            # Start Mumble Notes
            self.notes_process = subprocess.Popen(
                [sys.executable, script_path],
                env=env
            )
            
            # Update UI
            self.notes_status.setText("Mumble Notes: Running")
            self.notes_status.setStyleSheet("color: #27ae60; font-weight: bold;")
            self.notes_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            
            # Start monitoring thread
            self.notes_monitor = ProcessMonitorThread(self.notes_process, "notes")
            self.notes_monitor.process_stopped.connect(self.on_notes_stopped)
            self.notes_monitor.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Launch Error", f"Failed to launch Mumble Notes: {e}")
    
    def launch_quick(self):
        """Launch Mumble Quick application"""
        try:
            # Check if Notes is running and stop it if needed
            if self.notes_process and self.notes_process.poll() is None:
                reply = QMessageBox.question(
                    self, 'Stop Mumble Notes', 
                    'Mumble Notes is currently running. Stop it and launch Mumble Quick?',
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return
                self.terminate_notes()
                time.sleep(0.5)
            
            if self.quick_process and self.quick_process.poll() is None:
                QMessageBox.information(self, "Already Running", "Mumble Quick is already running.")
                return
            
            # Get the path to the script
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                      "mumble_quick", "app.py")
            
            # Set environment variable
            env = os.environ.copy()
            env["MUMBLE_DICTATION_TIMEOUT"] = "10"
            
            # Start Mumble Quick (hidden)
            if os.name == 'nt':  # Windows
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                self.quick_process = subprocess.Popen(
                    [sys.executable, script_path],
                    env=env,
                    startupinfo=startupinfo
                )
            else:  # Unix/Linux/Mac
                self.quick_process = subprocess.Popen(
                    [sys.executable, script_path],
                    env=env
                )
            
            # Update UI
            self.quick_status.setText("Mumble Quick: Running")
            self.quick_status.setStyleSheet("color: #27ae60; font-weight: bold;")
            self.quick_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            
            # Start monitoring thread
            self.quick_monitor = ProcessMonitorThread(self.quick_process, "quick")
            self.quick_monitor.process_stopped.connect(self.on_quick_stopped)
            self.quick_monitor.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Launch Error", f"Failed to launch Mumble Quick: {e}")
    
    def on_notes_stopped(self):
        """Handle when Mumble Notes process stops"""
        self.notes_status.setText("Mumble Notes: Not running")
        self.notes_status.setStyleSheet("color: #7f8c8d;")
        self.notes_button.setEnabled(True)
        self._check_stop_button_state()
    
    def on_quick_stopped(self):
        """Handle when Mumble Quick process stops"""
        self.quick_status.setText("Mumble Quick: Not running")
        self.quick_status.setStyleSheet("color: #7f8c8d;")
        self.quick_button.setEnabled(True)
        self._check_stop_button_state()
    
    def _check_stop_button_state(self):
        """Check if stop button should be enabled"""
        any_running = False
        if self.notes_process and self.notes_process.poll() is None:
            any_running = True
        if self.quick_process and self.quick_process.poll() is None:
            any_running = True
        self.stop_button.setEnabled(any_running)
    
    def terminate_notes(self):
        """Terminate Mumble Notes process"""
        try:
            if self.notes_process and self.notes_process.poll() is None:
                self.notes_process.terminate()
                # Wait a bit for graceful shutdown
                try:
                    self.notes_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.notes_process.kill()
                
                if self.notes_monitor:
                    self.notes_monitor.stop()
                    self.notes_monitor = None
                
                self.on_notes_stopped()
        except Exception as e:
            self.logger.error(f"Error terminating Mumble Notes: {e}")
    
    def terminate_quick(self):
        """Terminate Mumble Quick process"""
        try:
            if self.quick_process and self.quick_process.poll() is None:
                self.quick_process.terminate()
                # Wait a bit for graceful shutdown
                try:
                    self.quick_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.quick_process.kill()
                
                if self.quick_monitor:
                    self.quick_monitor.stop()
                    self.quick_monitor = None
                
                self.on_quick_stopped()
        except Exception as e:
            self.logger.error(f"Error terminating Mumble Quick: {e}")
    
    def terminate_processes(self):
        """Terminate all running processes"""
        self.terminate_notes()
        self.terminate_quick()
    
    def health_check(self):
        """Periodic health check for processes"""
        try:
            # Check notes process
            if self.notes_process and self.notes_process.poll() is not None:
                if self.notes_status.text() != "Mumble Notes: Not running":
                    self.on_notes_stopped()
            
            # Check quick process
            if self.quick_process and self.quick_process.poll() is not None:
                if self.quick_status.text() != "Mumble Quick: Not running":
                    self.on_quick_stopped()
        except Exception as e:
            self.logger.error(f"Error in health check: {e}")
    
    def open_documentation(self):
        """Open documentation in browser"""
        try:
            webbrowser.open("https://github.com/yourusername/mumble")
        except Exception as e:
            QMessageBox.information(
                self, "Help", 
                "Documentation: https://github.com/yourusername/mumble\n\n"
                "Mumble Notes: Full editor with speech-to-text\n"
                "Mumble Quick: Background voice input (Ctrl+Alt to activate)"
            )
    
    def closeEvent(self, event):
        """Handle window close event"""
        try:
            self.terminate_processes()
            if self.health_timer:
                self.health_timer.stop()
            event.accept()
        except Exception as e:
            self.logger.error(f"Error in closeEvent: {e}")
            event.accept()


def main():
    """Main function to run the launcher"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Mumble Launcher")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Mumble")
    
    # Create and show launcher
    launcher = MumbleLauncher()
    launcher.show()
    
    # Center window on screen
    screen = app.primaryScreen().geometry()
    window = launcher.geometry()
    x = (screen.width() - window.width()) // 2
    y = (screen.height() - window.height()) // 2
    launcher.move(x, y)
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main() 