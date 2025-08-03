#!/usr/bin/env python3
"""
Hearthstone Bot Launcher - Choose between GUI and command-line modes
"""

import sys
import os
import subprocess


def main():
    """Main launcher function - directly launches GUI"""
    try:
        print("Hearthstone Bot Launcher")
        print("=" * 40)
        print("Starting GUI mode...")
        
        # Check if tkinter is available
        import tkinter
        print("[OK] tkinter module found")
        
        # Try to import our modules
        print("[INFO] Importing bot modules...")
        import main_refactored
        print("[OK] Refactored bot modules imported successfully")
        
        # Start the GUI
        print("[INFO] Starting GUI...")
        main_refactored.main()
        
    except ImportError as e:
        print(f"[ERROR] Could not import bot modules: {e}")
        print("This might be due to missing dependencies.")
        print("Try running: pip install -r requirements.txt")
        print("Or run the setup script: setup_venv.bat")
    except Exception as e:
        print(f"[ERROR] Error starting GUI: {e}")
        print("Please check the error message above.")
    except KeyboardInterrupt:
        print("\n\nExiting...")


if __name__ == "__main__":
    main() 