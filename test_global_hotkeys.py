#!/usr/bin/env python3
"""
Test script for global hotkeys
"""

import keyboard
import time
import threading

def on_f10():
    print("F10 pressed - START/STOP")
    
def on_f12():
    print("F12 pressed - STOP")
    global running
    running = False

def main():
    global running
    running = True
    
    print("Testing global hotkeys...")
    print("Press F10 to simulate START/STOP")
    print("Press F12 to simulate STOP and exit")
    print("Press Ctrl+C to exit")
    
    # Register global hotkeys
    keyboard.add_hotkey('f10', on_f10, suppress=True)
    keyboard.add_hotkey('f12', on_f12, suppress=True)
    
    try:
        while running:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nCtrl+C pressed, exiting...")
    finally:
        # Cleanup
        keyboard.unhook_all()
        print("Global hotkeys unregistered")

if __name__ == "__main__":
    main() 