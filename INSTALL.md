# Installation Guide

## Quick Start

### Option 1: Windows (Easiest)
1. **Double-click `run.bat`** - This will automatically find Python and run the launcher
2. If Python is not found, follow the installation steps below

### Option 2: Manual Python Installation

#### Step 1: Install Python
1. Go to [python.org](https://python.org)
2. Download Python 3.8 or higher
3. **IMPORTANT**: Check "Add Python to PATH" during installation
4. Complete the installation

#### Step 2: Verify Installation
Open Command Prompt or PowerShell and run:
```bash
python --version
```
You should see something like: `Python 3.9.7`

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Run the Bot
```bash
python launcher.py
```

## Troubleshooting

### "Python is not recognized"
- Python is not in your PATH
- Reinstall Python and check "Add Python to PATH"
- Or restart your computer after installation

### "Module not found" errors
- Run: `pip install -r requirements.txt`
- Make sure you're in the correct directory

### GUI doesn't open
- Make sure tkinter is installed (usually comes with Python)
- Try running: `python -c "import tkinter; print('tkinter works')"`

### Test Everything Works
Run the test script:
```bash
python test_launcher.py
```

## File Structure
```
hearthstone_bot/
├── run.bat              # Windows launcher (double-click this!)
├── launcher.py          # Python launcher
├── main.py              # Command-line bot
├── ui.py                # GUI interface
├── test_launcher.py     # Test script
├── requirements.txt     # Python dependencies
└── README.md           # Full documentation
```

## Quick Commands

### Windows Users:
- **Double-click `run.bat`** (easiest)
- Or run: `python launcher.py`

### Command Line Users:
- Test: `python test_launcher.py`
- GUI: `python launcher.py` (then choose option 1)
- CLI: `python main.py --test`

## Need Help?

1. Run the test script: `python test_launcher.py`
2. Check the logs for error messages
3. Make sure Python is installed and in PATH
4. Install dependencies: `pip install -r requirements.txt` 