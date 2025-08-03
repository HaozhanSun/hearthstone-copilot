# Complete Dependencies Guide

## 🐍 Python Installation

### Required: Python 3.8 or higher
- **Download**: [python.org/downloads](https://python.org/downloads)
- **Installation**: Check "Add Python to PATH" during installation
- **Verify**: Run `python --version` in command prompt

## 📦 Python Packages (Auto-installed)

These will be installed automatically when you run `pip install -r requirements.txt`:

### Core Dependencies
- **opencv-python** (≥4.5.0) - Computer vision for image processing
- **pytesseract** (≥0.3.8) - OCR (Optical Character Recognition) for reading card text
- **pyautogui** (≥0.9.53) - Mouse and keyboard automation
- **numpy** (≥1.21.0) - Numerical computing (required by OpenCV)
- **pygetwindow** (≥0.0.9) - Window management and detection
- **pywin32** (≥300) - Windows API access
- **Pillow** (≥8.3.0) - Image processing library

### Optional Dependencies (for better performance)
- **opencv-contrib-python** - Additional OpenCV features
- **scikit-image** - Advanced image processing
- **matplotlib** - For debugging and visualization

## 🔧 External Software Dependencies

### Required: Tesseract OCR
**This is the most important external dependency!**

#### Windows Installation:
1. **Download**: [GitHub Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
2. **Install**: Run the installer
3. **Default Location**: `C:\Program Files\Tesseract-OCR\`
4. **Add to PATH**: 
   - Open System Properties → Environment Variables
   - Add `C:\Program Files\Tesseract-OCR\` to PATH
   - Or restart computer after installation

#### Verify Installation:
```bash
tesseract --version
```

### Optional: Hearthstone Game
- **Download**: [Battle.net](https://battle.net)
- **Install**: Hearthstone through Battle.net
- **Note**: The bot will work without Hearthstone running for testing

## 🚀 Quick Installation Commands

### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Install Optional Dependencies (Recommended)
```bash
pip install opencv-contrib-python scikit-image matplotlib
```

### Step 3: Verify Everything Works
```bash
python test_launcher.py
```

## 🔍 Dependency Verification Script

I've created a verification script to check all dependencies:

```bash
python test_launcher.py
```

This will test:
- ✅ Python installation
- ✅ Required modules
- ✅ File operations
- ✅ Launcher functionality

## 🛠️ Manual Installation Commands

If you prefer to install packages individually:

```bash
# Core packages
pip install opencv-python
pip install pytesseract
pip install pyautogui
pip install numpy
pip install pygetwindow
pip install pywin32
pip install Pillow

# Optional packages
pip install opencv-contrib-python
pip install scikit-image
pip install matplotlib
```

## 🐛 Common Issues & Solutions

### "tesseract is not recognized"
- **Solution**: Install Tesseract OCR and add to PATH
- **Alternative**: Restart computer after installation

### "cv2 module not found"
- **Solution**: `pip install opencv-python`
- **Alternative**: `pip install opencv-contrib-python`

### "pyautogui failsafe error"
- **Solution**: Move mouse to top-left corner to stop
- **Prevention**: Keep mouse away from screen corners

### "tkinter not found"
- **Solution**: Reinstall Python with tkinter (usually included)
- **Alternative**: `pip install tk`

### "Permission denied" errors
- **Solution**: Run as administrator
- **Alternative**: Use `pip install --user package_name`

## 📋 System Requirements

### Minimum Requirements:
- **OS**: Windows 10/11
- **Python**: 3.8 or higher
- **RAM**: 4GB
- **Storage**: 1GB free space
- **Display**: 1024x768 resolution

### Recommended Requirements:
- **OS**: Windows 10/11
- **Python**: 3.9 or higher
- **RAM**: 8GB
- **Storage**: 2GB free space
- **Display**: 1920x1080 resolution
- **Graphics**: Any modern GPU

## 🔧 Advanced Configuration

### Custom Tesseract Path
If Tesseract is installed in a non-standard location, add this to your script:

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Your\Custom\Path\tesseract.exe'
```

### OpenCV Optimization
For better performance, install:

```bash
pip install opencv-contrib-python
```

### GPU Acceleration (Optional)
For NVIDIA GPUs:

```bash
pip install opencv-python-gpu
```

## 📊 Dependency Check Script

Run this to verify all dependencies:

```python
import sys
import importlib

dependencies = [
    'cv2', 'pytesseract', 'pyautogui', 'numpy', 
    'pygetwindow', 'win32gui', 'PIL', 'tkinter'
]

print("Checking dependencies...")
for dep in dependencies:
    try:
        importlib.import_module(dep)
        print(f"✅ {dep}")
    except ImportError:
        print(f"❌ {dep} - MISSING")
```

## 🎯 Installation Checklist

- [ ] Python 3.8+ installed
- [ ] Python added to PATH
- [ ] Tesseract OCR installed
- [ ] Tesseract added to PATH
- [ ] Python packages installed (`pip install -r requirements.txt`)
- [ ] Test script runs successfully (`python test_launcher.py`)
- [ ] Launcher works (`python launcher.py`)
- [ ] GUI opens (`python ui.py`)

## 🆘 Need Help?

1. **Run the test script**: `python test_launcher.py`
2. **Check error messages** in the output
3. **Verify Python installation**: `python --version`
4. **Verify Tesseract**: `tesseract --version`
5. **Reinstall packages**: `pip install --force-reinstall -r requirements.txt` 