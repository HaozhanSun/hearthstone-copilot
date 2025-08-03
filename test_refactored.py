#!/usr/bin/env python3
"""
Test script for the refactored Hearthstone Bot architecture
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from core import BotController, BotState, BotContext
        print("✓ Core modules imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import core modules: {e}")
        return False
    
    try:
        from services import LoggingService, WindowService, OCRService, ScreenshotService
        print("✓ Service modules imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import service modules: {e}")
        return False
    
    try:
        from steps import (
            OCRManagementStep,
            BattleNetLaunchStep,
            PlayButtonStep,
            HearthstoneNavigationStep,
            CollectionAccessStep
        )
        print("✓ Step modules imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import step modules: {e}")
        return False
    
    try:
        from ui import MainWindow
        print("✓ UI modules imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import UI modules: {e}")
        return False
    
    return True


def test_services():
    """Test service initialization"""
    print("\nTesting services...")
    
    try:
        from services import LoggingService, WindowService, OCRService, ScreenshotService
        
        # Initialize logging service
        logger = LoggingService()
        print("✓ LoggingService initialized")
        
        # Initialize other services
        window_service = WindowService(logger)
        print("✓ WindowService initialized")
        
        ocr_service = OCRService(logger)
        print("✓ OCRService initialized")
        
        screenshot_service = ScreenshotService(logger)
        print("✓ ScreenshotService initialized")
        
        # Create services dictionary
        services = {
            'logger': logger,
            'window': window_service,
            'ocr': ocr_service,
            'screenshot': screenshot_service
        }
        
        print("✓ All services initialized successfully")
        return services
        
    except Exception as e:
        print(f"✗ Failed to initialize services: {e}")
        return None


def test_bot_controller(services):
    """Test bot controller initialization"""
    print("\nTesting bot controller...")
    
    try:
        from core import BotController
        
        bot_controller = BotController(services)
        print("✓ BotController initialized")
        
        # Test status methods
        status = bot_controller.get_status()
        print(f"✓ Bot status retrieved: {status['state']}")
        
        print("✓ Bot controller working correctly")
        return bot_controller
        
    except Exception as e:
        print(f"✗ Failed to initialize bot controller: {e}")
        return None


def test_steps(services):
    """Test step initialization"""
    print("\nTesting steps...")
    
    try:
        from steps import (
            OCRManagementStep,
            BattleNetLaunchStep,
            PlayButtonStep,
            HearthstoneNavigationStep,
            CollectionAccessStep
        )
        from core import BotContext
        
        # Test each step
        steps = [
            ("OCR Management", OCRManagementStep(services)),
            ("Battle.net Launch", BattleNetLaunchStep(services)),
            ("Play Button", PlayButtonStep(services)),
            ("Hearthstone Navigation", HearthstoneNavigationStep(services)),
            ("Collection Access", CollectionAccessStep(services))
        ]
        
        for step_name, step in steps:
            print(f"✓ {step_name} step initialized")
            
            # Test step name
            name = step.get_step_name()
            print(f"  - Step name: {name}")
            
            # Test can_skip method
            context = BotContext()
            can_skip = step.can_skip(context)
            print(f"  - Can skip: {can_skip}")
        
        print("✓ All steps working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Failed to test steps: {e}")
        return False


def main():
    """Main test function"""
    print("Hearthstone Bot - Refactored Architecture Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed. Please check the module structure.")
        return False
    
    # Test services
    services = test_services()
    if not services:
        print("\n❌ Service test failed.")
        return False
    
    # Test bot controller
    bot_controller = test_bot_controller(services)
    if not bot_controller:
        print("\n❌ Bot controller test failed.")
        return False
    
    # Test steps
    if not test_steps(services):
        print("\n❌ Step test failed.")
        return False
    
    print("\n" + "=" * 50)
    print("✅ All tests passed! The refactored architecture is working correctly.")
    print("\nYou can now run the refactored bot with:")
    print("python main_refactored.py")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 