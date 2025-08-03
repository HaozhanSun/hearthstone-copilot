# Hearthstone Bot

An automated script that recognizes cards and plays Hearthstone for you using computer vision and AI decision making.

## Features

- **Game Launch**: Automatically launches Hearthstone from the configured path
- **Window Detection**: Automatically finds and focuses the Hearthstone game window
- **Card Recognition**: Uses OCR and computer vision to identify cards in hand and on board
- **Game State Analysis**: Analyzes current mana, health, board state, and game phase
- **AI Decision Making**: Makes strategic decisions about which cards to play
- **Automation**: Safely controls mouse and keyboard to execute moves
- **Multiple Modes**: Analysis mode (view only) and auto-play mode
- **Path Configuration**: Easy configuration of Hearthstone installation path
- **CLI Monitoring**: Parallel command-line logging for monitoring bot progress

## Project Structure

```
hearthstone_bot/
├── venv/                    # Virtual environment (created by setup)
├── automation/              # Mouse/keyboard automation
│   ├── window_utils.py      # Window detection and screenshot capture
│   └── input_controller.py  # Safe input automation
├── card_recognition/        # Card detection and OCR
│   ├── card_detector.py     # Computer vision for card detection
│   ├── ocr_reader.py        # Text extraction from card images
│   └── card_database.py     # Card information database
├── game_state/             # Game state analysis
│   └── game_analyzer.py     # Analyzes current game situation
├── decision_engine/        # AI decision making
│   └── ai_engine.py        # Strategic move selection
├── main.py                 # Command-line bot controller
├── ui.py                   # GUI interface
├── launcher.py             # Interface chooser
├── setup_venv.bat          # 🆕 Virtual environment setup
├── activate_venv.bat       # 🆕 Activate virtual environment
├── run_with_venv.bat       # 🆕 Run bot with venv
├── run_cli_logger.bat      # 🆕 CLI monitoring tool
├── cli_logger.py           # 🆕 CLI logger implementation
├── check_dependencies.py   # Dependency checker
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # 🆕 Development dependencies
├── .gitignore             # 🆕 Git ignore file
├── README.md              # Main documentation
└── README_VENV.md         # 🆕 Virtual environment guide
```

## Prerequisites

### System Requirements
- Windows 10/11
- Python 3.8 or higher
- Hearthstone game installed and running

### Required Software
1. **Python**: Download from [python.org](https://python.org)
2. **Tesseract OCR**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - Install to default location (usually `C:\Program Files\Tesseract-OCR`)
   - Add to PATH environment variable
3. **Hearthstone**: Install and run the game

## Installation

### Option 1: Virtual Environment (Recommended)

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd hearthstone_bot
   ```

2. **Set up virtual environment (Windows)**
   ```bash
   # One-click setup
   setup_venv.bat
   
   # Or manually:
   python -m venv venv
   venv\Scripts\activate.bat
   pip install -r requirements.txt
   ```

3. **Run the bot**
   ```bash
   # One-click run
   run_with_venv.bat
   
   # Or manually:
   venv\Scripts\activate.bat
   python launcher.py
   ```

### Option 2: Global Installation (Legacy)

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd hearthstone_bot
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Tesseract installation**
   ```bash
   tesseract --version
   ```

## Configuration

### Battle.net and Hearthstone Path Setup

The bot needs to know where Battle.net and Hearthstone are installed. Edit `config.py` to set the correct paths:

```python
# Battle.net executable path
BATTLENET_PATH = r"E:\Battle.net\battle.net.exe"

# Hearthstone executable path (for verification)
HEARTHSTONE_PATH = r"E:\Battle.net\Hearthstone\Hearthstone.exe"
```

The bot will automatically try alternative common paths if the main paths are not found.

## Usage

### Quick Start

#### Option 1: GUI Mode (Recommended)
1. **Check paths** using the "Check HS Path" button
2. **Launch via Battle.net** using the "Launch via Battle.net" button
3. **Run the launcher** to choose your interface:
   ```bash
   python launcher.py
   ```
4. **Select GUI Mode** and click the "Detect Hearthstone Window" button
5. **Test components** to verify everything works
6. **Start analysis mode** to see what the bot detects
7. **Enable auto-play** when ready (use with caution!)

#### Option 2: Command Line Mode
1. **Start Hearthstone** and begin a game
2. **Run the bot in test mode** to verify everything works:
   ```bash
   python main.py --test
   ```

3. **Run in analysis mode** (view only, no gameplay):
   ```bash
   python main.py --debug
   ```

4. **Run in auto-play mode** (full automation):
   ```bash
   python main.py --auto-play --debug
   ```

#### Option 3: CLI Monitoring (Parallel to GUI)
1. **Start the CLI logger** in a separate terminal:
   ```bash
   # One-click CLI logger
   run_cli_logger.bat
   
   # Or manually:
   python cli_logger.py
   ```

2. **Use CLI commands** to monitor bot progress:
   - `start` - Start monitoring bot activity
   - `stop` - Stop monitoring
   - `status` - Show current bot status and recent screenshots
   - `help` - Show available commands
   - `quit` - Exit CLI logger

3. **Monitor in real-time** while the GUI bot is running

### GUI Features

The GUI provides a user-friendly interface with:
- **🚀 Launch via Battle.net**: Automatically launches Battle.net and clicks the PLAY button
- **🔍 Detect Window**: One-click Hearthstone window detection
- **🧪 Test Components**: Verify all bot components work correctly
- **📊 Analysis Mode**: Real-time game state analysis without playing
- **🎮 Auto-Play Mode**: Full automation with safety confirmations
- **📋 Status Display**: Live status indicators and game state information
- **📝 Log Viewer**: Real-time log display with save/clear options
- **🔧 Check HS Path**: Verify Battle.net and Hearthstone installation paths

### Command Line Options

- `--test`: Run component tests to verify everything works
- `--debug`: Enable detailed logging
- `--auto-play`: Enable automatic gameplay (use with caution!)

### Safety Features

- **Failsafe**: Move mouse to top-left corner to stop the bot
- **Manual Override**: Press Ctrl+C to stop the bot
- **GUI Controls**: Easy start/stop buttons with status indicators
- **Analysis Mode**: Use analysis mode to see what the bot detects without playing

## How It Works

### 1. Window Detection
The bot automatically finds the Hearthstone window and brings it to focus.

### 2. Screenshot Capture
Takes screenshots of the game window and extracts specific regions:
- Hand area (bottom)
- Board area (middle)
- Mana crystals (top-left)
- Health displays

### 3. Card Recognition
- **Computer Vision**: Detects card boundaries using contour detection
- **OCR**: Extracts card names, costs, and stats using Tesseract
- **Database Matching**: Matches recognized cards against a database

### 4. Game State Analysis
Analyzes:
- Cards in hand and their playability
- Minions on board (friendly and enemy)
- Current mana and turn number
- Game phase (mulligan, playing, etc.)

### 5. AI Decision Making
The AI considers:
- Board control and trading opportunities
- Mana efficiency
- Card synergies
- Defensive vs offensive plays

### 6. Automation
Safely executes moves using:
- Precise mouse clicking
- Card dragging
- Turn ending

## Configuration

### Card Database
The bot includes a basic card database. You can expand it by:
1. Adding more cards to `card_recognition/card_database.py`
2. Creating a custom database file
3. Implementing API integration with Hearthstone card databases

### AI Difficulty
Modify the AI behavior in `decision_engine/ai_engine.py`:
- Change `self.difficulty` to "easy", "medium", or "hard"
- Adjust decision weights and thresholds
- Add more sophisticated strategies

### Screen Regions
Adjust screen region detection in `automation/window_utils.py`:
- Modify the `regions` dictionary for different screen resolutions
- Calibrate for different Hearthstone UI layouts

## Troubleshooting

### Common Issues

1. **"Hearthstone window not found"**
   - Make sure Hearthstone is running
   - Try different window titles in `window_utils.py`

2. **"Tesseract not found"**
   - Install Tesseract OCR
   - Add to PATH environment variable
   - Restart command prompt

3. **Poor card recognition**
   - Ensure good lighting and contrast
   - Adjust OCR settings in `ocr_reader.py`
   - Add more cards to the database

4. **Incorrect mouse clicks**
   - Calibrate screen regions for your resolution
   - Check if Hearthstone is in windowed mode
   - Verify window focus

### Debug Mode
Use `--debug` flag to see detailed logs:
```bash
python main.py --debug
```

Logs are saved to `hearthstone_bot.log` for analysis.

## Safety and Ethics

### Important Disclaimers
- **Educational Purpose**: This bot is for educational purposes only
- **Terms of Service**: Using automation may violate Hearthstone's Terms of Service
- **Fair Play**: Consider the impact on other players
- **Risk**: Use at your own risk - account bans are possible

### Safe Usage
1. **Test First**: Always run in test mode first
2. **Analysis Mode**: Use analysis mode to understand what the bot sees
3. **Manual Override**: Keep your hand near the mouse for emergency stops
4. **Limited Use**: Don't run the bot for extended periods

## Development

### Adding New Features
1. **New Card Types**: Extend the card database and recognition
2. **Better AI**: Improve decision making algorithms
3. **UI Integration**: Add a graphical interface
4. **Statistics**: Track win rates and performance

### Contributing
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is for educational purposes only. Use at your own risk.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the debug logs
3. Test individual components
4. Open an issue with detailed information

---

**Remember**: This bot is for educational purposes. Use responsibly and consider the impact on the gaming community. 