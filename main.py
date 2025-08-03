#!/usr/bin/env python3
"""
Main entry point for the refactored Hearthstone Bot

This is the new main file that uses the modular architecture.
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import BotController, BotState
from services import LoggingService, WindowService, OCRService, ScreenshotService
from ui.main_window import MainWindow


def setup_services():
    """Setup all services"""
    # Initialize logging service first
    logger = LoggingService()
    
    # Initialize other services
    window_service = WindowService(logger)
    ocr_service = OCRService(logger)
    screenshot_service = ScreenshotService(logger)
    
    # Create services dictionary
    services = {
        'logger': logger,
        'window': window_service,
        'ocr': ocr_service,
        'screenshot': screenshot_service
    }
    
    return services


def main():
    """Main entry point"""
    try:
        # Setup services
        services = setup_services()
        logger = services['logger']
        
        logger.info("Starting Hearthstone Bot (Refactored Version)")
        
        # Initialize bot controller
        bot_controller = BotController(services)
        
        # Create and run GUI
        root = tk.Tk()
        app = MainWindow(root, bot_controller, services)
        
        # Handle window close
        def on_closing():
            if bot_controller.is_running():
                if messagebox.askokcancel("Quit", "Bot is still running. Do you want to stop it and quit?"):
                    bot_controller.stop()
                    app.cleanup()
                    root.destroy()
            else:
                app.cleanup()
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start the GUI
        root.mainloop()
        
    except Exception as e:
        print(f"Error starting bot: {e}")
        if 'logger' in locals():
            logger.error(f"Error starting bot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 