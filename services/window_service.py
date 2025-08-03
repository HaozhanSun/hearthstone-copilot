"""
Window management service for the Hearthstone Bot
"""

import time
import pygetwindow as gw
import pyautogui
from typing import Optional, List, Tuple
from core.exceptions import WindowNotFoundException


class WindowService:
    """Service for managing application windows"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def find_battlenet_window(self, max_attempts: int = 10) -> Optional[gw.Window]:
        """Find Battle.net window"""
        for attempt in range(max_attempts):
            try:
                battlenet_windows = gw.getWindowsWithTitle("Battle.net")
                if not battlenet_windows:
                    time.sleep(3)
                    continue
                
                # Find the main Battle.net window (larger one, not the initial small window)
                main_battlenet_window = None
                max_area = 0
                
                for window in battlenet_windows:
                    area = window.width * window.height
                    
                    # Prefer larger windows (main window) over smaller ones (initial window)
                    if area > max_area:
                        max_area = area
                        main_battlenet_window = window
                
                if main_battlenet_window:
                    # Validate window dimensions
                    if (main_battlenet_window.width > 0 and 
                        main_battlenet_window.height > 0 and
                        main_battlenet_window.height <= main_battlenet_window.width):  # Main window is wider than tall
                        return main_battlenet_window
                
                time.sleep(3)
                
            except Exception as e:
                self.logger.warning(f"Error finding Battle.net window (attempt {attempt + 1}): {e}")
                time.sleep(3)
        
        return None
    
    def find_hearthstone_window(self) -> Optional[gw.Window]:
        """Find Hearthstone window"""
        try:
            # Look for Hearthstone window - try Chinese name first, then English
            hearthstone_windows = gw.getWindowsWithTitle("炉石传说")
            if not hearthstone_windows:
                # Try English name as fallback, but be more specific to avoid our own GUI
                all_hearthstone_windows = gw.getWindowsWithTitle("Hearthstone")
                # Filter out our own GUI window more specifically
                hearthstone_windows = []
                for window in all_hearthstone_windows:
                    # Skip our own GUI window by checking for specific title patterns
                    if "Control Panel" in window.title or "Bot" in window.title:
                        continue
                    # Only include windows that look like the actual game
                    if window.title == "Hearthstone" or window.title.startswith("炉石传说"):
                        hearthstone_windows.append(window)
            
            if not hearthstone_windows:
                return None
            
            # Verify this is actually a Hearthstone game window
            for window in hearthstone_windows:
                # Skip windows that are too small to be the actual game
                if window.width < 800 or window.height < 600:
                    continue
                
                # Skip minimized windows
                if window.isMinimized:
                    continue
                
                return window
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error checking if Hearthstone is running: {e}")
            return None
    
    def is_hearthstone_running(self) -> bool:
        """Check if Hearthstone is already running"""
        return self.find_hearthstone_window() is not None
    
    def focus_window(self, window: gw.Window) -> bool:
        """Focus and activate a window"""
        try:
            # Try to refresh the window handle first
            try:
                window.activate()
            except Exception:
                # If the window handle is invalid, try to find it again
                self.logger.warning("Window handle appears invalid, attempting to refresh...")
                return False
            
            time.sleep(1)  # Wait for activation
            
            # Try a simpler focus approach
            try:
                window.activate()
                time.sleep(1)
                return True
            except Exception as e:
                self.logger.error(f"Error in simple window activation: {e}")
                return False
            
        except Exception as e:
            self.logger.error(f"Error focusing window: {e}")
            return False
    
    def get_window_region(self, window: gw.Window) -> Tuple[int, int, int, int]:
        """Get window region as (x, y, width, height)"""
        return (window.left, window.top, window.width, window.height)
    
    def click_in_window(self, window: gw.Window, x: int, y: int) -> bool:
        """Click at relative coordinates within a window"""
        try:
            # Convert relative coordinates to absolute screen coordinates
            abs_x = window.left + x
            abs_y = window.top + y
            
            pyautogui.click(abs_x, abs_y)
            return True
            
        except Exception as e:
            self.logger.error(f"Error clicking in window: {e}")
            return False
    
    def wait_for_window(self, window_title: str, timeout: int = 30) -> Optional[gw.Window]:
        """Wait for a window to appear"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                windows = gw.getWindowsWithTitle(window_title)
                if windows:
                    return windows[0]
                time.sleep(1)
            except Exception as e:
                self.logger.warning(f"Error waiting for window '{window_title}': {e}")
                time.sleep(1)
        
        return None 