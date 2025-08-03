# Virtual Environment Setup Guide

## 🐍 Why Virtual Environments?

Virtual environments provide **clean isolation** for Python projects by:
- ✅ Keeping project dependencies separate from system Python
- ✅ Preventing conflicts between different projects
- ✅ Making the project portable and reproducible
- ✅ Easy cleanup and reinstallation

## 🚀 Quick Start (Windows)

### Option 1: One-Click Setup
1. **Double-click `setup_venv.bat`** - This will create and configure everything
2. **Double-click `run_with_venv.bat`** - This will run the bot with the virtual environment

### Option 2: Manual Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Run the bot
python launcher.py
```

## 📁 New Project Structure

```
hearthstone_bot/
├── venv/                    # Virtual environment (created by setup)
├── automation/              # Mouse/keyboard automation
├── card_recognition/        # Card detection and OCR
├── game_state/             # Game state analysis
├── decision_engine/        # AI decision making
├── main.py                 # Command-line bot controller
├── ui.py                   # GUI interface
├── launcher.py             # Interface chooser
├── setup_venv.bat          # 🆕 Virtual environment setup
├── activate_venv.bat       # 🆕 Activate virtual environment
├── run_with_venv.bat       # 🆕 Run bot with venv
├── check_dependencies.py   # Dependency checker
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # 🆕 Development dependencies
├── .gitignore             # 🆕 Git ignore file
├── README.md              # Main documentation
└── README_VENV.md         # 🆕 This file
```

## 🔧 Available Scripts

### Setup Scripts
- **`setup_venv.bat`** - Creates virtual environment and installs dependencies
- **`activate_venv.bat`** - Activates virtual environment in new command prompt
- **`run_with_venv.bat`** - Activates venv and runs the bot launcher

### Legacy Scripts (Still Work)
- **`run.bat`** - Original launcher (doesn't use venv)
- **`launcher.py`** - Python launcher script

## 💻 Command Line Usage

### First Time Setup
```bash
# Create and setup virtual environment
setup_venv.bat

# Or manually:
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

### Daily Usage
```bash
# Option 1: Use the convenience script
run_with_venv.bat

# Option 2: Manual activation
activate_venv.bat

# Option 3: Manual commands
venv\Scripts\activate.bat
python launcher.py
```

### Development Setup
```bash
# Activate virtual environment
venv\Scripts\activate.bat

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest

# Format code
black .
flake8 .
```

## 🔍 Virtual Environment Commands

### Activation
```bash
# Windows
venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate
```

### Deactivation
```bash
deactivate
```

### Check if Active
```bash
# Look for (venv) in your prompt
# Or check Python path
where python
```

### Package Management
```bash
# List installed packages
pip list

# Install new package
pip install package_name

# Install from requirements
pip install -r requirements.txt

# Update requirements file
pip freeze > requirements.txt
```

## 🧹 Cleanup and Maintenance

### Recreate Virtual Environment
```bash
# Remove old environment
rmdir /s venv

# Create new one
setup_venv.bat
```

### Update Dependencies
```bash
# Activate environment
venv\Scripts\activate.bat

# Update packages
pip install --upgrade -r requirements.txt
```

### Check for Outdated Packages
```bash
pip list --outdated
```

## 🐛 Troubleshooting

### "venv not found"
- Run `setup_venv.bat` to create the virtual environment

### "pip not found"
- Make sure virtual environment is activated
- Run `python -m pip install package_name`

### "Permission denied"
- Run command prompt as administrator
- Or use `pip install --user package_name`

### "Module not found"
- Activate virtual environment first
- Install missing package: `pip install package_name`

### "Python path issues"
- Always activate virtual environment before running scripts
- Use `venv\Scripts\activate.bat` on Windows

## 🔄 Migration from Global Installation

If you previously installed packages globally:

1. **Create virtual environment**
   ```bash
   setup_venv.bat
   ```

2. **Test everything works**
   ```bash
   run_with_venv.bat
   ```

3. **Uninstall global packages (optional)**
   ```bash
   pip uninstall opencv-python pytesseract pyautogui numpy pygetwindow pywin32 Pillow
   ```

## 📦 Package Management

### Production Dependencies
```bash
# Install production dependencies
pip install -r requirements.txt
```

### Development Dependencies
```bash
# Install development tools
pip install -r requirements-dev.txt
```

### Custom Packages
```bash
# Add new package to requirements.txt
pip install new_package
pip freeze > requirements.txt
```

## 🎯 Best Practices

1. **Always activate virtual environment** before running the bot
2. **Use `run_with_venv.bat`** for easiest experience
3. **Keep requirements.txt updated** when adding new packages
4. **Don't commit venv folder** (it's in .gitignore)
5. **Use development requirements** for coding tools

## 🆚 Comparison: With vs Without Virtual Environment

### Without Virtual Environment
- ❌ Packages installed globally
- ❌ Risk of conflicts with other projects
- ❌ Hard to reproduce environment
- ❌ Difficult to clean up

### With Virtual Environment
- ✅ Isolated dependencies
- ✅ No conflicts with other projects
- ✅ Easy to reproduce environment
- ✅ Simple cleanup (just delete venv folder)
- ✅ Better project portability

## 🚀 Next Steps

1. **Run setup**: `setup_venv.bat`
2. **Test installation**: `run_with_venv.bat`
3. **Start developing**: Activate venv and run your scripts
4. **Install dev tools**: `pip install -r requirements-dev.txt`

The virtual environment setup makes the project much more professional and maintainable! 🎉 