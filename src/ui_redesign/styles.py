"""
Centralized styling system for the modern Mumble UI
Dark theme with blue/purple accents and glassmorphism effects
"""

# Color Palette
COLORS = {
    # Dark theme colors
    'background': '#1a1a1a',
    'card_bg': 'rgba(40, 40, 45, 0.95)',
    'card_border': 'rgba(60, 60, 65, 0.8)',
    
    # Text colors
    'text_primary': '#ffffff',
    'text_secondary': '#b8b8b8',
    'text_muted': '#8a8a8a',
    'text_accent': '#64b5f6',
    
    # Accent colors
    'accent_blue': '#2196f3',
    'accent_purple': '#9c27b0',
    'accent_green': '#4caf50',  # For waiting state
    'accent_red': '#f44336',    # For active/recording state
    'accent_gradient': 'qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2196f3, stop:1 #9c27b0)',
    
    # Status colors
    'success': '#4caf50',
    'warning': '#ff9800',
    'error': '#f44336',
    
    # Interactive states
    'hover': 'rgba(255, 255, 255, 0.1)',
    'pressed': 'rgba(255, 255, 255, 0.15)',
    'focus_glow': 'rgba(33, 150, 243, 0.3)',
}

# Font configuration
FONTS = {
    'family': 'Inter, Segoe UI, Roboto, sans-serif',
    'sizes': {
        'small': '11px',
        'medium': '13px',
        'large': '16px',
        'header': '20px',
        'title': '24px',
    },
    'weights': {
        'normal': '400',
        'medium': '500',
        'bold': '600',
    }
}

# Common styling components
CARD_STYLE = f"""
    background: {COLORS['card_bg']};
    border: 1px solid {COLORS['card_border']};
    border-radius: 16px;
    backdrop-filter: blur(20px);
"""

BUTTON_BASE = f"""
    QPushButton {{
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-family: {FONTS['family']};
        font-size: {FONTS['sizes']['medium']};
        font-weight: {FONTS['weights']['medium']};
        color: {COLORS['text_primary']};
    }}
    QPushButton:hover {{
        background: {COLORS['hover']};
    }}
    QPushButton:pressed {{
        background: {COLORS['pressed']};
    }}
"""

# Complete stylesheet for the launcher
LAUNCHER_STYLE = f"""
    QDialog {{
        background: transparent;
    }}
    
    QFrame#card {{
        {CARD_STYLE}
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
    }}
    
    QLabel#header {{
        color: {COLORS['text_primary']};
        font-family: {FONTS['family']};
        font-size: {FONTS['sizes']['header']};
        font-weight: {FONTS['weights']['bold']};
        padding: 20px 0 10px 0;
    }}
    
    QLineEdit#search {{
        background: rgba(255, 255, 255, 0.05);
        border: 2px solid transparent;
        border-radius: 12px;
        padding: 16px 20px;
        color: {COLORS['text_primary']};
        font-family: {FONTS['family']};
        font-size: {FONTS['sizes']['large']};
        selection-background-color: {COLORS['accent_blue']};
    }}
    QLineEdit#search:focus {{
        border: 2px solid {COLORS['accent_blue']};
        box-shadow: 0 0 20px {COLORS['focus_glow']};
    }}
    QLineEdit#search::placeholder {{
        color: {COLORS['text_muted']};
    }}
    
    QPushButton#action_button {{
        background: transparent;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 16px 20px;
        text-align: left;
        color: {COLORS['text_primary']};
        font-family: {FONTS['family']};
        font-size: {FONTS['sizes']['medium']};
        margin: 4px 0;
    }}
    QPushButton#action_button:hover {{
        background: {COLORS['hover']};
        border: 1px solid rgba(255, 255, 255, 0.2);
    }}
    QPushButton#action_button:pressed {{
        background: {COLORS['pressed']};
    }}
    QPushButton#action_button:disabled {{
        background: rgba(255, 255, 255, 0.02);
        color: {COLORS['text_muted']};
        border: 1px solid rgba(255, 255, 255, 0.05);
    }}
    
    QLabel#warning {{
        color: {COLORS['warning']};
        font-family: {FONTS['family']};
        font-size: {FONTS['sizes']['small']};
        padding: 10px;
        background: rgba(255, 152, 0, 0.1);
        border-radius: 8px;
        border: 1px solid rgba(255, 152, 0, 0.3);
    }}
    
    QLabel#icon {{
        color: {COLORS['text_secondary']};
        font-size: 18px;
    }}
    
    QLabel#hotkey {{
        color: {COLORS['text_muted']};
        font-family: {FONTS['family']};
        font-size: {FONTS['sizes']['small']};
        background: rgba(255, 255, 255, 0.05);
        border-radius: 4px;
        padding: 4px 8px;
    }}
"""

# Listening UI styles
LISTENING_STYLE = f"""
    QDialog {{
        background: transparent;
    }}
    
    QFrame#card {{
        {CARD_STYLE}
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.6);
    }}
    
    QLabel#listening_header {{
        color: {COLORS['accent_blue']};
        font-family: {FONTS['family']};
        font-size: {FONTS['sizes']['title']};
        font-weight: {FONTS['weights']['bold']};
        padding: 20px 0;
    }}
    
    QLabel#instruction {{
        color: {COLORS['text_secondary']};
        font-family: {FONTS['family']};
        font-size: {FONTS['sizes']['medium']};
        padding: 20px 0;
    }}
"""

# Notes editor styles
NOTES_STYLE = f"""
    QWidget {{
        background: transparent;
    }}
    
    QFrame#card {{
        {CARD_STYLE}
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
    }}
    
    QLabel#notes_header {{
        color: {COLORS['text_primary']};
        font-family: {FONTS['family']};
        font-size: {FONTS['sizes']['header']};
        font-weight: {FONTS['weights']['bold']};
        padding: 20px 0 10px 0;
    }}
    
    QPlainTextEdit#editor {{
        background: transparent;
        border: none;
        color: {COLORS['text_primary']};
        font-family: {FONTS['family']};
        font-size: {FONTS['sizes']['medium']};
        line-height: 1.6;
        padding: 20px;
        selection-background-color: {COLORS['accent_blue']};
    }}
    QPlainTextEdit#editor::placeholder {{
        color: {COLORS['text_muted']};
    }}
    
    QPushButton#save_button {{
        background: {COLORS['accent_gradient']};
        border: none;
        border-radius: 8px;
        padding: 12px 32px;
        color: {COLORS['text_primary']};
        font-family: {FONTS['family']};
        font-size: {FONTS['sizes']['medium']};
        font-weight: {FONTS['weights']['medium']};
    }}
    QPushButton#save_button:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1976d2, stop:1 #7b1fa2);
    }}
    QPushButton#save_button:pressed {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1565c0, stop:1 #6a1b9a);
    }}
    
    QPushButton#copy_button {{
        background: transparent;
        border: 2px solid {COLORS['accent_blue']};
        border-radius: 8px;
        padding: 10px 32px;
        color: {COLORS['accent_blue']};
        font-family: {FONTS['family']};
        font-size: {FONTS['sizes']['medium']};
        font-weight: {FONTS['weights']['medium']};
    }}
    QPushButton#copy_button:hover {{
        background: rgba(33, 150, 243, 0.1);
    }}
    QPushButton#copy_button:pressed {{
        background: rgba(33, 150, 243, 0.2);
    }}
    
    QPushButton#close_button {{
        background: transparent;
        border: none;
        border-radius: 8px;
        padding: 12px 32px;
        color: {COLORS['text_muted']};
        font-family: {FONTS['family']};
        font-size: {FONTS['sizes']['medium']};
        font-weight: {FONTS['weights']['medium']};
    }}
    QPushButton#close_button:hover {{
        background: {COLORS['hover']};
        color: {COLORS['text_secondary']};
    }}
    QPushButton#close_button:pressed {{
        background: {COLORS['pressed']};
    }}
"""

def apply_shadow_effect(widget, blur_radius=25, offset=(0, 10)):
    """Apply drop shadow effect to a widget"""
    from PyQt5.QtWidgets import QGraphicsDropShadowEffect
    from PyQt5.QtCore import QPointF
    from PyQt5.QtGui import QColor
    
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur_radius)
    shadow.setColor(QColor(0, 0, 0, 100))
    shadow.setOffset(QPointF(offset[0], offset[1]))
    widget.setGraphicsEffect(shadow)

def create_icon(unicode_char, size=18, color=COLORS['text_secondary']):
    """Create a text-based icon using Unicode characters"""
    from PyQt5.QtWidgets import QLabel
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont
    
    icon = QLabel(unicode_char)
    icon.setObjectName("icon")
    icon.setAlignment(Qt.AlignCenter)
    icon.setFixedSize(size + 4, size + 4)
    font = QFont()
    font.setPointSize(size)
    icon.setFont(font)
    icon.setStyleSheet(f"color: {color}; font-size: {size}px;")
    return icon 