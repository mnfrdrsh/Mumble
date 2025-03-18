"""
Shared logging configuration for Mumble applications
"""

import os
import logging
from datetime import datetime
from typing import Optional

def setup_logging(app_name: str, log_level: int = logging.INFO) -> logging.Logger:
    """
    Set up logging configuration for Mumble applications
    
    Args:
        app_name: Name of the application (e.g., 'notes' or 'quick')
        log_level: Logging level to use
        
    Returns:
        Logger instance for the application
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Create log file name with timestamp
    log_file = os.path.join(log_dir, f"mumble_{app_name}_{datetime.now().strftime('%Y%m%d')}.log")
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Create logger
    logger = logging.getLogger(f'mumble.{app_name}')
    logger.setLevel(log_level)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger 