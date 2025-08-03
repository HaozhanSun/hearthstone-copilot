#!/usr/bin/env python3
"""
Dependency Checker for Hearthstone Bot
This script checks if all required dependencies are installed and working.
"""

import sys
import subprocess
import importlib
from pathlib import Path


def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("   ✅ Python version is compatible")
        return True
    else:
        print("   ❌ Python 3.8+ required")
        return False


def check_python_packages():
    """Check if required Python packages are installed"""
    print("\n📦 Checking Python packages...")
    
    required_packages = {
        'cv2': 'opencv-python',
        'pytesseract': 'pytesseract',
        'pyautogui': 'pyautogui',
        'numpy': 'numpy',
        'pygetwindow': 'pygetwindow',
        'win32gui': 'pywin32',
        'PIL': 'Pillow',
        'tkinter': 'tkinter (built-in)'
    }
    
    optional_packages = {
        'skimage': 'scikit-image',
        'matplotlib': 'matplotlib'
    }
    
    all_good = True
    
    # Check required packages
    print("   Required packages:")
    for module, package in required_packages.items():
        try:
            importlib.import_module(module)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - MISSING")
            all_good = False
    
    # Check optional packages
    print("   Optional packages:")
    for module, package in optional_packages.items():
        try:
            importlib.import_module(module)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ⚠️  {package} - Not installed (optional)")
    
    return all_good


def check_tesseract():
    """Check if Tesseract OCR is installed"""
    print("\n🔍 Checking Tesseract OCR...")
    
    try:
        # Try to run tesseract command
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"   ✅ Tesseract found: {version_line}")
            return True
        else:
            print("   ❌ Tesseract command failed")
            return False
    except FileNotFoundError:
        print("   ❌ Tesseract not found in PATH")
        print("   💡 Install from: https://github.com/UB-Mannheim/tesseract/wiki")
        return False
    except subprocess.TimeoutExpired:
        print("   ❌ Tesseract command timed out")
        return False
    except Exception as e:
        print(f"   ❌ Error checking Tesseract: {e}")
        return False


def check_files():
    """Check if required files exist"""
    print("\n📁 Checking project files...")
    
    required_files = [
        'main.py',
        'ui.py',
        'launcher.py',
        'requirements.txt',
        'automation/__init__.py',
        'card_recognition/__init__.py',
        'game_state/__init__.py',
        'decision_engine/__init__.py'
    ]
    
    all_good = True
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MISSING")
            all_good = False
    
    return all_good


def check_hearthstone_window():
    """Check if Hearthstone window can be detected"""
    print("\n🎮 Checking Hearthstone window detection...")
    
    try:
        import pygetwindow as gw
        
        # Look for Hearthstone windows
        hearthstone_windows = []
        for window in gw.getAllWindows():
            title = window.title.lower()
            if 'hearthstone' in title or '炉石' in title:
                hearthstone_windows.append(window.title)
        
        if hearthstone_windows:
            print(f"   ✅ Found Hearthstone windows: {hearthstone_windows}")
            return True
        else:
            print("   ⚠️  No Hearthstone windows found (game may not be running)")
            return True  # Not an error, just informational
    except Exception as e:
        print(f"   ❌ Error checking windows: {e}")
        return False


def test_basic_functionality():
    """Test basic bot functionality"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Test screenshot capability
        import pyautogui
        screenshot = pyautogui.screenshot()
        print(f"   ✅ Screenshot capture works ({screenshot.size})")
        
        # Test OpenCV
        import cv2
        import numpy as np
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        gray = cv2.cvtColor(test_image, cv2.COLOR_RGB2GRAY)
        print("   ✅ OpenCV image processing works")
        
        # Test OCR (basic)
        import pytesseract
        # This will fail if Tesseract is not installed, but that's OK
        print("   ✅ pytesseract module loaded")
        
        return True
    except Exception as e:
        print(f"   ❌ Basic functionality test failed: {e}")
        return False


def provide_installation_commands():
    """Provide installation commands for missing dependencies"""
    print("\n🔧 Installation Commands:")
    print("   If any dependencies are missing, run these commands:")
    print()
    print("   # Install Python packages:")
    print("   pip install -r requirements.txt")
    print()
    print("   # Install optional packages:")
    print("   pip install opencv-contrib-python scikit-image matplotlib")
    print()
    print("   # Install Tesseract OCR:")
    print("   # Download from: https://github.com/UB-Mannheim/tesseract/wiki")
    print("   # Make sure to add to PATH during installation")


def main():
    """Main dependency check function"""
    print("🔧 Hearthstone Bot - Dependency Checker")
    print("=" * 50)
    
    # Run all checks
    checks = [
        ("Python Version", check_python_version),
        ("Python Packages", check_python_packages),
        ("Tesseract OCR", check_tesseract),
        ("Project Files", check_files),
        ("Window Detection", check_hearthstone_window),
        ("Basic Functionality", test_basic_functionality)
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        try:
            if check_func():
                passed += 1
            else:
                print(f"❌ {check_name} check failed")
        except Exception as e:
            print(f"❌ {check_name} check failed with exception: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Check Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All dependencies are installed and working!")
        print("   You can now run: python launcher.py")
    else:
        print("❌ Some dependencies are missing or not working.")
        print("   Please install missing dependencies and run this check again.")
        provide_installation_commands()
    
    print("\n💡 Next steps:")
    print("   1. Run: python test_launcher.py")
    print("   2. Run: python launcher.py")
    print("   3. Start Hearthstone and test the bot!")


if __name__ == "__main__":
    main() 