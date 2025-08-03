# Hearthstone Copilot Bot

An automated Hearthstone bot with a refactored modular architecture that provides efficient game automation using computer vision and OCR technology.

## Features

- **Modular Architecture**: Clean, maintainable codebase with separated concerns
- **Game Launch**: Automatically launches Hearthstone from Battle.net
- **Window Management**: Intelligent window detection and focus management
- **OCR Integration**: Uses Umi-OCR for accurate text recognition
- **State Machine**: Robust step-by-step execution with error handling
- **GUI Interface**: Modern Tkinter-based user interface
- **Comprehensive Logging**: Detailed logging with GUI integration
- **Error Recovery**: Automatic retry mechanisms and graceful error handling

## Project Structure

```
hearthstone_bot/
├── core/                    # Core bot functionality
│   ├── __init__.py         # Core module exports
│   ├── bot_state.py        # State management (BotState, BotContext)
│   ├── bot_controller.py   # Main bot orchestrator
│   └── exceptions.py       # Custom exception classes
├── services/               # Service layer
│   ├── __init__.py         # Services module exports
│   ├── window_service.py   # Window management and interaction
│   ├── ocr_service.py      # OCR operations and text detection
│   ├── screenshot_service.py # Screenshot capture and processing
│   └── logging_service.py  # Centralized logging system
├── steps/                  # Bot workflow steps
│   ├── __init__.py         # Steps module exports
│   ├── base_step.py        # Abstract base class for all steps
│   ├── ocr_management.py   # OCR service management
│   ├── battlenet_launch.py # Battle.net application launch
│   ├── play_button.py      # PLAY button detection and clicking
│   ├── hearthstone_nav.py  # Hearthstone navigation
│   └── collection_access.py # Collection access
├── ui/                     # User interface
│   ├── __init__.py         # UI module exports
│   ├── main_window.py      # Main GUI window
│   ├── components/         # UI components
│   └── dialogs/            # Dialog windows
├── utils/                  # Utility functions
│   ├── __init__.py         # Utils module exports
│   ├── image_utils.py      # Image processing utilities
│   ├── text_utils.py       # Text processing utilities
│   └── config_utils.py     # Configuration utilities
├── main.py                 # Main entry point
├── launcher.py             # Application launcher
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules
└── README.md              # This documentation
```

## Architecture Overview

### Core Components

- **BotState**: Enum defining bot states (IDLE, STARTING, RUNNING, etc.)
- **BotContext**: Data class holding bot execution context and state
- **BotController**: Main orchestrator that manages step execution
- **Custom Exceptions**: Structured error handling hierarchy

### Service Layer

- **WindowService**: Manages application windows (Battle.net, Hearthstone)
- **OCRService**: Handles text recognition using Umi-OCR
- **ScreenshotService**: Captures and processes screenshots
- **LoggingService**: Centralized logging with GUI integration

### Step Classes

Each step implements the `BaseStep` interface:
- **OCRManagementStep**: Ensures OCR service is running
- **BattleNetLaunchStep**: Launches Battle.net application
- **PlayButtonStep**: Finds and clicks the PLAY button
- **HearthstoneNavigationStep**: Navigates to Hearthstone home screen
- **CollectionAccessStep**: Accesses the card collection

## Prerequisites

### System Requirements
- Windows 10/11
- Python 3.8 or higher
- Battle.net and Hearthstone installed

### Required Software
1. **Python**: Download from [python.org](https://python.org)
2. **Umi-OCR**: Included in the project (Umi-OCR_Rapid_v2.1.5)
3. **Battle.net**: Install from [battle.net](https://battle.net)
4. **Hearthstone**: Install via Battle.net

## Installation

### Quick Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/HaozhanSun/hearthstone-copilot.git
   cd hearthstone-copilot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the bot**
   ```bash
   python launcher.py
   ```

### Virtual Environment (Recommended)

1. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate.bat
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the bot**
   ```bash
   python launcher.py
   ```

## Configuration

### Battle.net Path

The bot automatically detects Battle.net installation. If it's not found, you can configure the path in the code:

```python
# In services/window_service.py
BATTLENET_PATHS = [
    r"E:\Battle.net\battle.net.exe",  # Add your path here
    r"C:\Program Files (x86)\Battle.net\Battle.net Launcher.exe",
    # ... other common paths
]
```

## Usage

### GUI Mode (Recommended)

1. **Launch the application**
   ```bash
   python launcher.py
   ```

2. **Use the GUI interface**
   - Click "Start Bot" to begin automation
   - Monitor progress in the log viewer
   - Click "Stop Bot" to halt execution

### Command Line Mode

```bash
python main.py
```

## How It Works

### 1. Initialization
- Sets up all services (logging, window, OCR, screenshot)
- Initializes the bot controller with step classes
- Creates the GUI interface

### 2. Step Execution
The bot executes steps sequentially:

1. **OCR Management**: Ensures Umi-OCR service is running
2. **Battle.net Launch**: Launches Battle.net (skipped if Hearthstone is running)
3. **Play Button**: Finds and clicks the PLAY button
4. **Hearthstone Navigation**: Navigates to home screen
5. **Collection Access**: Accesses the card collection

### 3. Error Handling
- Each step has retry mechanisms
- Comprehensive error logging with stack traces
- Graceful degradation on failures

### 4. State Management
- Tracks bot progress through `BotContext`
- Maintains step-specific data
- Provides status updates to GUI

## Key Features

### Modular Design
- **Separation of Concerns**: Each module has a specific responsibility
- **Dependency Injection**: Services are passed to components
- **Testability**: Each component can be tested independently
- **Maintainability**: Easy to modify and extend

### Robust Error Handling
- **Custom Exceptions**: Structured error hierarchy
- **Retry Mechanisms**: Automatic retry with exponential backoff
- **Stack Traces**: Detailed error information for debugging
- **Graceful Degradation**: Continues operation when possible

### Advanced OCR
- **Umi-OCR Integration**: High-accuracy text recognition
- **Chinese Character Support**: Special handling for Chinese text
- **Individual Character Detection**: Precise character-level recognition
- **Region-based Search**: Efficient text search in specific areas

### Window Management
- **Intelligent Detection**: Finds windows by title and properties
- **Focus Management**: Ensures windows are properly focused
- **Handle Refresh**: Refreshes invalid window handles
- **Size Validation**: Filters windows by size and state

## Development

### Adding New Steps

1. **Create a new step class**
   ```python
   from steps.base_step import BaseStep
   
   class MyNewStep(BaseStep):
       def execute(self, context: BotContext) -> BotContext:
           # Implementation here
           return context
   ```

2. **Add to bot controller**
   ```python
   # In core/bot_controller.py
   self.steps.append(MyNewStep(self.services))
   ```

### Adding New Services

1. **Create service class**
   ```python
   class MyService:
       def __init__(self, logger):
           self.logger = logger
   ```

2. **Register in main.py**
   ```python
   services['my_service'] = MyService(logger)
   ```

### Testing

```bash
# Test individual components
python -c "from core import BotController; print('Core imports work')"
python -c "from services import WindowService; print('Services work')"
python -c "from steps import BaseStep; print('Steps work')"
```

## Troubleshooting

### Common Issues

1. **"Umi-OCR service not found"**
   - Ensure Umi-OCR is in the project directory
   - Check if the service is running on port 1224

2. **"Battle.net window not found"**
   - Verify Battle.net is installed
   - Check the path configuration

3. **"Hearthstone not launching"**
   - Ensure Hearthstone is installed via Battle.net
   - Check if the PLAY button is visible

4. **"OCR not working"**
   - Verify Umi-OCR is running
   - Check the service status

### Debug Mode

The bot includes comprehensive logging:
- All operations are logged with timestamps
- Error stack traces are captured
- Debug screenshots are saved for analysis
- GUI log viewer shows real-time progress

## Safety and Ethics

### Important Disclaimers
- **Educational Purpose**: This bot is for educational purposes only
- **Terms of Service**: Using automation may violate Hearthstone's Terms of Service
- **Fair Play**: Consider the impact on other players
- **Risk**: Use at your own risk - account bans are possible

### Safe Usage
1. **Test First**: Always test in a safe environment
2. **Monitor**: Keep an eye on the bot's behavior
3. **Manual Override**: Be ready to stop the bot if needed
4. **Limited Use**: Don't run for extended periods

## License

This project is for educational purposes only. Use at your own risk.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in the GUI
3. Test individual components
4. Open an issue with detailed information

---

**Remember**: This bot is for educational purposes. Use responsibly and consider the impact on the gaming community. 