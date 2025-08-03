# Hearthstone Bot - Refactored Architecture

## Overview

The Hearthstone Bot has been completely refactored from a monolithic design to a modular, maintainable architecture following industry best practices.

## New Architecture

### Directory Structure

```
hearthstone_bot/
├── core/                          # Core bot logic
│   ├── __init__.py
│   ├── bot_state.py              # State machine and context management
│   ├── bot_controller.py         # Main bot orchestration
│   └── exceptions.py             # Custom exceptions
├── steps/                        # Individual bot steps
│   ├── __init__.py
│   ├── base_step.py              # Abstract base class for all steps
│   ├── ocr_management.py         # OCR service management
│   ├── battlenet_launch.py       # Battle.net launching
│   ├── play_button.py            # PLAY button detection/clicking
│   ├── hearthstone_nav.py        # Hearthstone navigation
│   └── collection_access.py      # Collection access
├── services/                     # Service layer
│   ├── __init__.py
│   ├── window_service.py         # Window detection and management
│   ├── ocr_service.py            # OCR operations
│   ├── screenshot_service.py     # Screenshot capture and processing
│   └── logging_service.py        # Centralized logging
├── ui/                          # GUI components
│   ├── __init__.py
│   ├── main_window.py           # Main GUI window
│   ├── components/              # Reusable UI components
│   └── dialogs/                 # Modal dialogs
├── utils/                       # Utility functions
│   ├── __init__.py
│   ├── image_utils.py           # Image processing utilities
│   ├── text_utils.py            # Text processing utilities
│   └── config_utils.py          # Configuration utilities
├── main_refactored.py           # New entry point
└── ui.py                        # Original monolithic file (kept for reference)
```

## Key Design Principles

### 1. Separation of Concerns
- **Core**: State management and bot orchestration
- **Steps**: Individual workflow steps with clear responsibilities
- **Services**: Reusable functionality (OCR, window management, etc.)
- **UI**: Completely separated from bot logic

### 2. State Machine Pattern
- Clear state transitions: `IDLE` → `STARTING` → `CHECKING_OCR` → `LAUNCHING_BATTLENET` → etc.
- Each step can update the bot state
- Context object tracks step data, errors, and progress

### 3. Dependency Injection
- Services are injected into steps rather than tightly coupled
- Easy to mock services for testing
- Clear service interfaces

### 4. Error Recovery
- Each step has retry logic with configurable max attempts
- Centralized error handling
- Graceful degradation when services fail

### 5. Testability
- Each component can be unit tested independently
- Clear interfaces and separation of concerns
- Mock services for testing

## Core Components

### BotController
The main orchestrator that:
- Manages the bot lifecycle
- Executes steps in sequence
- Handles state transitions
- Provides status information

### BotContext
Tracks the bot's execution state:
- Current state and step
- Step data and progress
- Error messages and retry counts
- Elapsed time

### BaseStep
Abstract base class for all steps:
- Common error handling
- Retry logic
- Pre/post execution hooks
- Step name and skip logic

## Service Layer

### LoggingService
- Centralized logging with multiple outputs (file, console, GUI)
- Thread-safe log queue for GUI updates
- Structured log entries with timestamps

### WindowService
- Window detection and management
- Focus and activation
- Coordinate conversion
- Window waiting and validation

### OCRService
- Umi-OCR integration
- Text detection with language support
- Chinese character extraction
- Region-based text search

### ScreenshotService
- Screenshot capture and processing
- Image preprocessing for OCR
- Debug screenshot saving
- Image annotation utilities

## Step Classes

### OCRManagementStep
- Checks if Umi-OCR is running
- Launches OCR service if needed
- Waits for service availability

### BattleNetLaunchStep
- Launches Battle.net application
- Waits for window to appear
- Can be skipped if Hearthstone is already running

### PlayButtonStep
- Finds and clicks the PLAY button in Battle.net
- Verifies click success
- Handles "playing now" status

### HearthstoneNavigationStep
- Waits for Hearthstone to launch
- Navigates to home screen
- Handles "点击开始" button detection
- Can skip if already at home screen

### CollectionAccessStep
- Clicks the collection button
- Verifies collection access
- Takes final confirmation screenshot

## Usage

### Running the Refactored Bot

```bash
# Run the new refactored version
python main_refactored.py

# Or run the original version (for comparison)
python ui.py
```

### Key Benefits

1. **Maintainability**: Each component has a single responsibility
2. **Extensibility**: Easy to add new steps or modify existing ones
3. **Testability**: Each component can be tested independently
4. **Error Handling**: Robust error recovery and retry logic
5. **State Tracking**: Clear visibility into bot progress and state
6. **Modularity**: Services can be reused across different steps

### Migration Path

The refactoring maintains backward compatibility:
- Original `ui.py` still works
- New architecture is in separate files
- Gradual migration possible
- Both versions can coexist

## Future Enhancements

1. **Configuration Management**: Move hardcoded values to config files
2. **Plugin System**: Allow custom steps to be added
3. **Web Interface**: Add web-based control panel
4. **Database Integration**: Store bot history and statistics
5. **Advanced Error Recovery**: More sophisticated retry strategies
6. **Performance Monitoring**: Track step execution times and success rates

## Testing

Each component can be tested independently:

```python
# Test a service
from services import OCRService
from services import LoggingService

logger = LoggingService()
ocr = OCRService(logger)
# Test OCR functionality

# Test a step
from steps import PlayButtonStep
from core import BotContext

step = PlayButtonStep(services)
context = BotContext()
# Test step execution
```

This refactored architecture provides a solid foundation for future development while maintaining all the functionality of the original bot. 