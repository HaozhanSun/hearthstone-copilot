"""
Centralized logging service for the Hearthstone Bot
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from queue import Queue
import threading


class LoggingService:
    """Centralized logging service"""
    
    def __init__(self, log_dir: str = "logs", max_log_size: int = 1024 * 1024):  # 1MB
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.max_log_size = max_log_size
        self.log_queue = Queue()
        self.gui_callbacks = []
        
        # Setup file logging
        self._setup_file_logging()
        
        # Setup console logging
        self._setup_console_logging()
    
    def _setup_file_logging(self):
        """Setup file logging"""
        log_file = self.log_dir / "bot.log"
        
        # Create file handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Add to root logger
        logging.getLogger().addHandler(file_handler)
        logging.getLogger().setLevel(logging.INFO)
    
    def _setup_console_logging(self):
        """Setup console logging"""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        logging.getLogger().addHandler(console_handler)
    
    def add_gui_callback(self, callback):
        """Add GUI callback for real-time logging"""
        self.gui_callbacks.append(callback)
    
    def remove_gui_callback(self, callback):
        """Remove GUI callback"""
        if callback in self.gui_callbacks:
            self.gui_callbacks.remove(callback)
    
    def log(self, level: str, message: str, **kwargs):
        """Log a message with additional context"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Create log entry
        log_entry = {
            'timestamp': timestamp,
            'level': level.upper(),
            'message': message,
            **kwargs
        }
        
        # Add to queue for GUI
        self.log_queue.put(log_entry)
        
        # Call GUI callbacks
        for callback in self.gui_callbacks:
            try:
                callback(log_entry)
            except Exception as e:
                # Don't let GUI callback errors break logging
                print(f"GUI callback error: {e}")
        
        # Use standard logging
        logger = logging.getLogger()
        if level.upper() == 'DEBUG':
            logger.debug(message)
        elif level.upper() == 'INFO':
            logger.info(message)
        elif level.upper() == 'WARNING':
            logger.warning(message)
        elif level.upper() == 'ERROR':
            logger.error(message)
        elif level.upper() == 'CRITICAL':
            logger.critical(message)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.log('DEBUG', message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.log('INFO', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.log('WARNING', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.log('ERROR', message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self.log('CRITICAL', message, **kwargs)
    
    def get_log_queue(self) -> Queue:
        """Get the log queue for GUI consumption"""
        return self.log_queue
    
    def save_debug_screenshot(self, screenshot, attempt_type: str, success: bool, 
                            details: str = "", subfolder: str = "") -> Optional[str]:
        """Save a screenshot for debugging"""
        try:
            import cv2
            
            # Create timestamp for filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            
            # Create filename with details
            status = "SUCCESS" if success else "FAILED"
            filename = f"{timestamp}_{attempt_type}_{status}.png"
            
            # Create subfolder path if specified
            if subfolder:
                screenshot_dir = self.log_dir / "screenshots" / "debug" / subfolder
            else:
                screenshot_dir = self.log_dir / "screenshots" / "debug"
            
            # Ensure directory exists
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            
            # Full path
            filepath = screenshot_dir / filename
            
            # Save screenshot
            cv2.imwrite(str(filepath), screenshot)
            
            # Log the save
            self.info(f"Debug screenshot saved: {filename} - {details}")
            
            return str(filepath)
            
        except Exception as e:
            self.error(f"Error saving debug screenshot: {e}")
            return None 