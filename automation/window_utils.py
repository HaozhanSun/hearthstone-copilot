import pygetwindow as gw
import win32gui
import pyautogui
import cv2
import numpy as np
from PIL import Image
import time


def find_hearthstone_window():
    """Find and return the Hearthstone game window"""
    # Try different possible window titles
    possible_titles = [
        "Hearthstone",
        "炉石传说",
        "Hearthstone Heroes of Warcraft"
    ]
    
    for title in possible_titles:
        windows = gw.getWindowsWithTitle(title)
        if windows:
            return windows[0]
    
    # If not found by exact title, search for partial matches
    for window in gw.getAllWindows():
        if "hearthstone" in window.title.lower() or "炉石" in window.title:
            return window
    
    return None


def focus_hearthstone_window():
    """Focus the Hearthstone window and bring it to front"""
    window = find_hearthstone_window()
    if window:
        window.restore()  # Unminimize if minimized
        window.activate()  # Bring to front
        time.sleep(0.5)  # Give time for window to focus
        return True
    return False


def get_hearthstone_screenshot():
    """Capture a screenshot of the Hearthstone window"""
    window = find_hearthstone_window()
    if not window:
        return None
    
    # Get window position and size
    x, y, width, height = window.left, window.top, window.width, window.height
    
    # Capture screenshot
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    return np.array(screenshot)


def get_game_region_screenshot(region_name):
    """Capture screenshot of specific game regions"""
    window = find_hearthstone_window()
    if not window:
        return None
    
    # Define regions relative to window size
    regions = {
        'hand': (0.1, 0.7, 0.8, 0.25),  # Bottom 25% of screen, 80% width
        'board': (0.1, 0.3, 0.8, 0.4),  # Middle 40% of screen, 80% width
        'mana': (0.05, 0.05, 0.15, 0.1),  # Top-left corner
        'opponent_hand': (0.1, 0.05, 0.8, 0.15),  # Top 15% of screen
        'hero_power': (0.85, 0.6, 0.1, 0.15),  # Bottom-right corner
    }
    
    if region_name not in regions:
        return None
    
    rel_x, rel_y, rel_w, rel_h = regions[region_name]
    x = int(window.left + window.width * rel_x)
    y = int(window.top + window.height * rel_y)
    width = int(window.width * rel_w)
    height = int(window.height * rel_h)
    
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    return np.array(screenshot)


def focus_battlenet_cn():
    # Try to find the Battle.net China window by title
    for w in gw.getAllTitles():
        if "Battle.net" in w or "战网" in w:
            window = gw.getWindowsWithTitle(w)[0]
            window.restore()  # Unminimize if minimized
            window.activate()  # Bring to front
            return True
    return False


if __name__ == "__main__":
    # Test window detection
    if focus_hearthstone_window():
        print("Hearthstone window focused!")
        
        # Test screenshot capture
        screenshot = get_hearthstone_screenshot()
        if screenshot is not None:
            print(f"Screenshot captured: {screenshot.shape}")
            
            # Save test screenshot
            cv2.imwrite("test_screenshot.png", cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR))
            print("Test screenshot saved as 'test_screenshot.png'")
    else:
        print("Hearthstone window not found.") 