#!/usr/bin/env python3
"""
Configuration file for Hearthstone Bot
"""

import os

# Battle.net executable path
BATTLENET_PATH = r"E:\Battle.net\battle.net.exe"

# Alternative Battle.net paths to try if the main path doesn't exist
ALTERNATIVE_BATTLENET_PATHS = [
    r"C:\Program Files (x86)\Battle.net\battle.net.exe",
    r"C:\Program Files\Battle.net\battle.net.exe",
    r"D:\Battle.net\battle.net.exe",
    r"F:\Battle.net\battle.net.exe",
]

# Hearthstone executable path (for verification)
HEARTHSTONE_PATH = r"E:\Battle.net\Hearthstone\Hearthstone.exe"

# Alternative paths to try if the main path doesn't exist
ALTERNATIVE_PATHS = [
    r"C:\Program Files (x86)\Battle.net\Hearthstone\Hearthstone.exe",
    r"C:\Program Files\Battle.net\Hearthstone\Hearthstone.exe",
    r"D:\Battle.net\Hearthstone\Hearthstone.exe",
    r"F:\Battle.net\Hearthstone\Hearthstone.exe",
]

# Game settings
GAME_SETTINGS = {
    'screenshot_delay': 0.5,  # Delay between screenshots in seconds
    'click_delay': 0.1,       # Delay between clicks in seconds
    'analysis_interval': 2.0,  # How often to analyze game state in seconds
    'auto_play_speed': 1.0,    # Speed of auto-play actions in seconds
}

# OCR settings
OCR_SETTINGS = {
    'confidence_threshold': 0.7,  # Minimum confidence for OCR text recognition
    'tesseract_config': '--oem 3 --psm 6',
    'preprocessing_enabled': True,
}

# AI settings
AI_SETTINGS = {
    'difficulty': 'medium',  # easy, medium, hard
    'aggressive_mode': False,
    'conservative_mode': False,
}

def get_battlenet_path():
    """Get the Battle.net executable path, trying alternatives if needed"""
    if os.path.exists(BATTLENET_PATH):
        return BATTLENET_PATH
    
    for path in ALTERNATIVE_BATTLENET_PATHS:
        if os.path.exists(path):
            return path
    
    return BATTLENET_PATH  # Return default even if not found

def get_hearthstone_path():
    """Get the Hearthstone executable path, trying alternatives if needed"""
    if os.path.exists(HEARTHSTONE_PATH):
        return HEARTHSTONE_PATH
    
    for path in ALTERNATIVE_PATHS:
        if os.path.exists(path):
            return path
    
    return HEARTHSTONE_PATH  # Return default even if not found

def validate_battlenet_path():
    """Check if Battle.net executable exists at any known location"""
    return os.path.exists(get_battlenet_path())

def validate_hearthstone_path():
    """Check if Hearthstone executable exists at any known location"""
    return os.path.exists(get_hearthstone_path())

def update_hearthstone_path(new_path):
    """Update the Hearthstone path (for future use)"""
    global HEARTHSTONE_PATH
    HEARTHSTONE_PATH = new_path 