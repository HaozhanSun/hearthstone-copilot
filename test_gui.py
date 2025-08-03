#!/usr/bin/env python3
"""
Simple GUI Test Script
This script tests if the GUI can be launched successfully.
"""

import sys
import traceback

def test_gui():
    """Test if the GUI can be launched"""
    print("Testing GUI Launch...")
    print("=" * 40)
    
    try:
        # Test 1: Check if tkinter is available
        print("1. Testing tkinter import...")
        import tkinter
        print("   [OK] tkinter imported successfully")
        
        # Test 2: Check if our modules can be imported
        print("2. Testing bot module imports...")
        from automation.window_utils import focus_hearthstone_window
        print("   [OK] automation.window_utils imported")
        
        from game_state.game_analyzer import GameAnalyzer
        print("   [OK] game_state.game_analyzer imported")
        
        from decision_engine.ai_engine import AIEngine
        print("   [OK] decision_engine.ai_engine imported")
        
        from automation.input_controller import InputController
        print("   [OK] automation.input_controller imported")
        
        # Test 3: Import the GUI module
        print("3. Testing GUI module import...")
        import ui
        print("   [OK] GUI module imported successfully")
        
        # Test 4: Try to create a simple GUI window
        print("4. Testing GUI window creation...")
        root = tkinter.Tk()
        root.withdraw()  # Hide the window
        print("   [OK] GUI window created successfully")
        
        # Test 5: Try to create the main GUI
        print("5. Testing main GUI creation...")
        gui = ui.HearthstoneBotGUI(root)
        print("   [OK] Main GUI created successfully")
        
        root.destroy()
        print("   [OK] GUI window destroyed successfully")
        
        print("\n" + "=" * 40)
        print("[SUCCESS] All GUI tests passed!")
        print("The GUI should work correctly.")
        return True
        
    except ImportError as e:
        print(f"   [ERROR] Import error: {e}")
        print("\nThis might be due to missing dependencies.")
        print("Try running: pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"   [ERROR] Unexpected error: {e}")
        print("\nFull error details:")
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("GUI Test Script")
    print("=" * 40)
    
    success = test_gui()
    
    if success:
        print("\n[SUCCESS] GUI is ready to use!")
        print("You can now run: python launcher.py")
        print("And choose option 1 for GUI mode.")
    else:
        print("\n[ERROR] GUI test failed.")
        print("Please check the error messages above.")
        print("Make sure all dependencies are installed.")

    input("Press Enter to exit...")


if __name__ == "__main__":
    main() 