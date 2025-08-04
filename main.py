#!/usr/bin/env python3
"""
Main entry point for the refactored Hearthstone Bot

This is the new main file that uses the modular architecture.
"""

import sys
import os
import signal
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
    # Global variables for cleanup
    global root, app, bot_controller, logger
    
    def signal_handler(signum, frame):
        """Handle Ctrl+C and other signals"""
        try:
            logger.info(f"Received signal {signum}, cleaning up...")
            if 'bot_controller' in globals() and bot_controller.is_running():
                bot_controller.stop()
            if 'app' in globals():
                app.cleanup()
            if 'root' in globals():
                root.destroy()
            os._exit(0)
        except Exception as e:
            print(f"Error during signal cleanup: {e}")
            os._exit(1)
    
    # Set up signal handlers (only in main thread)
    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    except ValueError as e:
        # Signal handlers can only be set in the main thread
        logger.warning(f"Could not set signal handlers: {e}")
    
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
            try:
                logger.info("=== WINDOW CLOSE HANDLER START ===")
                
                # Always cleanup first with timeout
                logger.info("Calling app.cleanup()...")
                import threading
                import time
                
                # Run cleanup in a separate thread with timeout
                cleanup_complete = threading.Event()
                cleanup_error = None
                
                def cleanup_worker():
                    nonlocal cleanup_error
                    try:
                        app.cleanup()
                        cleanup_complete.set()
                    except Exception as e:
                        cleanup_error = e
                        cleanup_complete.set()
                
                cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
                cleanup_thread.start()
                
                # Wait for cleanup with timeout
                if cleanup_complete.wait(timeout=5):  # 5 second timeout
                    if cleanup_error:
                        logger.error(f"Cleanup failed: {cleanup_error}")
                    else:
                        logger.info("App.cleanup() completed")
                else:
                    logger.warning("Cleanup timeout - forcing exit anyway")
                
                # Stop bot if running
                if bot_controller.is_running():
                    logger.info("Bot is running, asking user...")
                    if messagebox.askokcancel("Quit", "Bot is still running. Do you want to stop it and quit?"):
                        logger.info("User confirmed, stopping bot...")
                        bot_controller.stop()
                        logger.info("Bot stopped")
                
                # Destroy window
                logger.info("Destroying root window...")
                root.destroy()
                logger.info("Root window destroyed")
                
                # Force exit immediately
                logger.info("Calling os._exit(0) from window close handler...")
                import os
                os._exit(0)
                
            except Exception as e:
                logger.error(f"Error during window close: {e}")
                # Force exit even if there's an error
                logger.info("Calling os._exit(1) due to error...")
                import os
                os._exit(1)
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start the GUI
        try:
            logger.info("Starting mainloop...")
            root.mainloop()
            logger.info("Mainloop ended normally")
        except Exception as e:
            logger.error(f"Error in mainloop: {e}")
        finally:
            # Ensure cleanup happens even if mainloop fails
            logger.info("Mainloop finally block - ensuring cleanup...")
            try:
                app.cleanup()
                logger.info("App cleanup completed in finally block")
            except Exception as e:
                logger.error(f"Error in app cleanup in finally block: {e}")
            logger.info("Calling os._exit(0) to force exit")
            os._exit(0)
        
    except Exception as e:
        print(f"Error starting bot: {e}")
        if 'logger' in locals():
            logger.error(f"Error starting bot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 