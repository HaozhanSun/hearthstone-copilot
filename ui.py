#!/usr/bin/env python3
"""
Hearthstone Bot GUI - User-friendly interface for the Hearthstone bot

This GUI provides:
- Window detection button
- Component testing
- Analysis mode
- Auto-play mode
- Real-time status display
- Log viewer
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import queue
import time
import sys
import os
from datetime import datetime
import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
import keyboard

# Import our bot components
from automation.window_utils import focus_hearthstone_window, get_hearthstone_screenshot
from game_state.game_analyzer import GameAnalyzer
from decision_engine.ai_engine import AIEngine
from automation.input_controller import InputController
from config import get_battlenet_path, get_hearthstone_path, validate_battlenet_path, validate_hearthstone_path


class HearthstoneBotGUI:
    """Main GUI class for the Hearthstone bot"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Hearthstone Bot - Control Panel")
        self.root.geometry("1200x700")  # Increased from 800x600 for better layout
        self.root.resizable(True, True)
        
        # Bot components
        self.game_analyzer = None
        self.ai_engine = None
        self.input_controller = None
        
        # Threading
        self.running = False
        self.analysis_thread = None
        self.auto_play_thread = None
        self.log_queue = queue.Queue()
        
        # Bot state
        self.bot_running = False
        self.stop_event = threading.Event()
        
        # Setup GUI
        self.setup_gui()
        self.setup_logging()
        
        # Setup global hotkeys
        self.setup_global_hotkeys()
        
        # Start log consumer
        self.consume_logs()
    
    def setup_gui(self):
        """Setup the main GUI layout with logs on the right side"""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for 2-column layout with fixed left panel width
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, minsize=400)  # Left column (controls and game state) - fixed minimum width
        main_frame.columnconfigure(1, weight=1)  # Right column (logs) - expandable
        main_frame.rowconfigure(2, weight=1)     # Make rows expandable
        
        # Title (spans both columns)
        title_label = ttk.Label(main_frame, text="Hearthstone Bot Control Panel", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Control buttons frame (left column)
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Configure control frame for better button layout
        for i in range(4):  # 4 columns for buttons
            control_frame.columnconfigure(i, weight=1)
        
        # Make buttons wider by setting minimum width
        button_style = ttk.Style()
        button_style.configure('Wide.TButton', padding=(10, 5))
        
        # Row 1: Main control buttons
        # Start/Stop button
        self.start_btn = ttk.Button(control_frame, text="START (F10)", 
                                   command=self.toggle_bot, style='Wide.TButton')
        self.start_btn.grid(row=0, column=0, padx=(0, 5), pady=5, sticky=(tk.W, tk.E))
        
        # Window detection button
        self.detect_btn = ttk.Button(control_frame, text="Detect Hearthstone Window", 
                                    command=self.detect_window, style='Wide.TButton')
        self.detect_btn.grid(row=0, column=1, padx=(0, 5), pady=5, sticky=(tk.W, tk.E))
        
        # Test components button
        self.test_btn = ttk.Button(control_frame, text="Test Components", 
                                  command=self.test_components, style='Wide.TButton')
        self.test_btn.grid(row=0, column=2, padx=(0, 5), pady=5, sticky=(tk.W, tk.E))
        
        # Check path button
        self.check_path_btn = ttk.Button(control_frame, text="Check HS Path", 
                                        command=self.check_hearthstone_path, style='Wide.TButton')
        self.check_path_btn.grid(row=0, column=3, padx=(0, 5), pady=5, sticky=(tk.W, tk.E))
        
        # Row 2: Mode buttons and OCR checkbox
        # Analysis mode button
        self.analysis_btn = ttk.Button(control_frame, text="Start Analysis Mode", 
                                      command=self.toggle_analysis_mode, style='Wide.TButton')
        self.analysis_btn.grid(row=1, column=0, padx=(0, 5), pady=5, sticky=(tk.W, tk.E))
        
        # Auto-play mode button
        self.autoplay_btn = ttk.Button(control_frame, text="Start Auto-Play", 
                                      command=self.toggle_auto_play, style='Wide.TButton')
        self.autoplay_btn.grid(row=1, column=1, padx=(0, 5), pady=5, sticky=(tk.W, tk.E))
        
        # OCR checkbox
        self.ocr_var = tk.BooleanVar(value=True)
        self.ocr_checkbox = ttk.Checkbutton(control_frame, text="Auto-launch Umi-OCR", 
                                           variable=self.ocr_var)
        self.ocr_checkbox.grid(row=1, column=2, columnspan=2, padx=(0, 5), pady=5, sticky=(tk.W, tk.E))
        
        # Bind local hotkeys (for when GUI is focused)
        self.root.bind('<F10>', lambda e: self.toggle_bot())
        self.root.bind('<F12>', lambda e: self.stop_bot())
        
        # Status frame (left column)
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        # Status indicators with better spacing and wider layout
        ttk.Label(status_frame, text="Window Detection:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.window_status = ttk.Label(status_frame, text="Not Detected", foreground="red", font=("Arial", 9))
        self.window_status.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(status_frame, text="Bot Status:", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.bot_status = ttk.Label(status_frame, text="Stopped", foreground="orange", font=("Arial", 9))
        self.bot_status.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(status_frame, text="Mode:", font=("Arial", 9, "bold")).grid(row=2, column=0, sticky=tk.W, pady=2)
        self.mode_status = ttk.Label(status_frame, text="None", foreground="gray", font=("Arial", 9))
        self.mode_status.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(status_frame, text="Umi-OCR Status:", font=("Arial", 9, "bold")).grid(row=3, column=0, sticky=tk.W, pady=2)
        self.ocr_status = ttk.Label(status_frame, text="Not Running", foreground="red", font=("Arial", 9))
        self.ocr_status.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Game state frame (left column)
        game_frame = ttk.LabelFrame(main_frame, text="Game State", padding="10")
        game_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        game_frame.columnconfigure(0, weight=1)
        game_frame.rowconfigure(1, weight=1)
        
        # Game state treeview
        columns = ("Property", "Value")
        self.game_tree = ttk.Treeview(game_frame, columns=columns, show="headings", height=8)
        self.game_tree.heading("Property", text="Property")
        self.game_tree.heading("Value", text="Value")
        self.game_tree.column("Property", width=200)  # Increased from 150
        self.game_tree.column("Value", width=300)     # Increased from 200
        self.game_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for game state
        game_scrollbar = ttk.Scrollbar(game_frame, orient=tk.VERTICAL, command=self.game_tree.yview)
        game_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.game_tree.configure(yscrollcommand=game_scrollbar.set)
        
        # Log frame (right column, full height)
        log_frame = ttk.LabelFrame(main_frame, text="Logs", padding="10")
        log_frame.grid(row=0, column=1, rowspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Log text area (takes most of the space)
        self.log_text = scrolledtext.ScrolledText(log_frame, width=150)  # Increased from 60 to 100 for wider logs
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Log controls (bottom of log frame)
        log_controls = ttk.Frame(log_frame)
        log_controls.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Button(log_controls, text="Clear Logs", command=self.clear_logs).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(log_controls, text="Save Logs", command=self.save_logs).pack(side=tk.LEFT)
        
        # Initialize game state display
        self.update_game_state_display({})
    
    def setup_logging(self):
        """Setup logging to capture messages in the GUI"""
        import logging
        
        class QueueHandler(logging.Handler):
            def __init__(self, queue):
                super().__init__()
                self.queue = queue
            
            def emit(self, record):
                self.queue.put(record)
        
        # Create queue handler
        queue_handler = QueueHandler(self.log_queue)
        queue_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        # Add to root logger
        logging.getLogger().addHandler(queue_handler)
        logging.getLogger().setLevel(logging.INFO)
    
    def setup_global_hotkeys(self):
        """Setup global hotkeys that work even when GUI is not focused"""
        try:
            # Register global hotkeys
            keyboard.add_hotkey('f10', self.toggle_bot, suppress=True)
            keyboard.add_hotkey('f12', self.stop_bot, suppress=True)
            self.log_message("Global hotkeys registered: F10 (START/STOP), F12 (STOP)")
        except Exception as e:
            self.log_message(f"Warning: Could not register global hotkeys: {e}")
            self.log_message("Hotkeys will only work when GUI is focused")
    
    def consume_logs(self):
        """Consume logs from queue and display in GUI"""
        try:
            while True:
                record = self.log_queue.get_nowait()
                msg = self.format_log_record(record)
                self.log_text.insert(tk.END, msg + "\n")
                self.log_text.see(tk.END)
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.consume_logs)
    
    def format_log_record(self, record):
        """Format log record for display"""
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        level = record.levelname
        message = record.getMessage()
        return f"[{timestamp}] {level}: {message}"
    
    def save_debug_screenshot(self, screenshot, attempt_type, success, details="", subfolder=""):
        """Save a screenshot for debugging image recognition"""
        try:
            # Create timestamp for filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]  # Include milliseconds
            
            # Create filename with details
            status = "SUCCESS" if success else "FAILED"
            filename = f"{timestamp}_{attempt_type}_{status}.png"
            
            # Create subfolder path if specified
            if subfolder:
                screenshot_dir = os.path.join("screenshots", "image_recognition_attempts", subfolder)
            else:
                screenshot_dir = os.path.join("screenshots", "image_recognition_attempts")
            
            # Ensure directory exists
            os.makedirs(screenshot_dir, exist_ok=True)
            
            # Full path
            filepath = os.path.join(screenshot_dir, filename)
            
            # Save screenshot
            cv2.imwrite(filepath, screenshot)
            
            # Log the save
            self.log_message(f"Debug screenshot saved: {filename} - {details}")
            
            return filepath
            
        except Exception as e:
            self.log_message(f"Error saving debug screenshot: {e}")
            return None
    
    def toggle_bot(self):
        """Toggle bot on/off"""
        if not hasattr(self, 'bot_running') or not self.bot_running:
            self.start_bot()
        else:
            self.stop_bot()
    
    def start_bot(self):
        """Start the bot"""
        self.bot_running = True
        self.start_btn.config(text="STOP (F12)")
        self.log_message("Bot started - Press F12 to stop")
        self.bot_status.config(text="Running", foreground="green")
        
        # Start the bot process
        self.bot_thread = threading.Thread(target=self._run_bot)
        self.bot_thread.daemon = True
        self.bot_thread.start()
    
    def stop_bot(self):
        """Stop the bot"""
        self.bot_running = False
        self.start_btn.config(text="START (F10)")
        self.log_message("Bot stopped")
        self.bot_status.config(text="Stopped", foreground="orange")
    
    def _run_bot(self):
        """Main bot process"""
        try:
            self.log_message("Starting bot process...")
            
            # Step 1: Manage OCR
            if not self._manage_ocr():
                self.log_message("OCR management failed, but continuing...")
            
            # Step 2: Check if Hearthstone is already running
            if self._is_hearthstone_running():
                self.log_message("Hearthstone is already running, skipping Battle.net step")
            else:
                # Step 2: Launch Battle.net
                if not self._launch_battlenet():
                    self.log_message("Failed to launch Battle.net")
                    return
                
                # Step 3: Find and click PLAY button
                if not self._find_and_click_play_button():
                    self.log_message("Failed to find PLAY button")
                    return
            
            # Step 4: Verify Hearthstone launched
            if not self._verify_hearthstone_launched():
                self.log_message("Failed to verify Hearthstone launch")
                return
            
            self.log_message("Bot process completed successfully! Reached Hearthstone collection and stopped.")
            
        except Exception as e:
            self.log_message(f"Error in bot process: {e}")
    
    def _launch_battlenet(self):
        """Launch Battle.net"""
        try:
            import subprocess
            import os
            
            # Get Battle.net executable path from config
            battlenet_path = get_battlenet_path()
            
            # Check if Battle.net exists
            if not os.path.exists(battlenet_path):
                return False
            
            # Launch Battle.net
            subprocess.Popen([battlenet_path], shell=True)
            
            # Wait for Battle.net to start
            time.sleep(5)
            return True
            
        except Exception as e:
            return False
    
    def _is_hearthstone_running(self):
        """Check if Hearthstone is already running"""
        try:
            import pygetwindow as gw
            
            # Look for Hearthstone window - try Chinese name first, then English
            hearthstone_windows = gw.getWindowsWithTitle("炉石传说")
            if not hearthstone_windows:
                # Try English name as fallback, but be more specific to avoid our own GUI
                all_hearthstone_windows = gw.getWindowsWithTitle("Hearthstone")
                # Filter out our own GUI window more specifically
                hearthstone_windows = []
                for window in all_hearthstone_windows:
                    # Skip our own GUI window by checking for specific title patterns
                    if "Control Panel" in window.title or "Bot" in window.title:
                        continue
                    # Only include windows that look like the actual game
                    if window.title == "Hearthstone" or window.title.startswith("炉石传说"):
                        hearthstone_windows.append(window)
                
                if not hearthstone_windows:
                    return False
            
            # Verify this is actually a Hearthstone game window
            for window in hearthstone_windows:
                # Skip windows that are too small to be the actual game
                if window.width < 800 or window.height < 600:
                    continue
                
                # Skip minimized windows
                if window.isMinimized:
                    continue
                
                return True
            
            return False
            
        except Exception as e:
            self.log_message(f"Error checking if Hearthstone is running: {e}")
            return False
    
    def _manage_ocr(self):
        """Manage Umi-OCR service - check if running, launch if needed"""
        try:
            import subprocess
            import os
            import psutil
            import requests
            
            # First check if Umi-OCR HTTP service is responding
            try:
                response = requests.get("http://127.0.0.1:1224/", timeout=3)
                if response.status_code == 200:
                    self.ocr_status.config(text="Service Running", foreground="green")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            # If service not responding, check if Umi-OCR process is running
            umi_ocr_running = False
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    if proc.info['exe'] and 'Umi-OCR' in proc.info['exe']:
                        umi_ocr_running = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if umi_ocr_running:
                self.ocr_status.config(text="Process Found", foreground="orange")
                return True
            
            # If not running and checkbox is enabled, launch Umi-OCR
            if self.ocr_var.get():
                ocr_path = "Umi-OCR/Umi-OCR_Rapid_v2.1.5/UmiOCR-data/RUN_GUI.bat"
                if os.path.exists(ocr_path):
                    subprocess.Popen([ocr_path], shell=True)
                    time.sleep(3)  # Give it time to start
                    
                    # Check if service is now responding
                    try:
                        response = requests.get("http://127.0.0.1:1224/", timeout=5)
                        if response.status_code == 200:
                            self.ocr_status.config(text="Service Running", foreground="green")
                            return True
                    except requests.exceptions.RequestException:
                        pass
                    
                    self.ocr_status.config(text="Launched", foreground="orange")
                    return True
                else:
                    self.ocr_status.config(text="Not Found", foreground="red")
                    return False
            else:
                self.ocr_status.config(text="Disabled", foreground="gray")
                return True
                
        except Exception as e:
            self.ocr_status.config(text="Error", foreground="red")
            return False
    
    def _find_and_click_play_button(self):
        """Find and click the PLAY button within Battle.net window using OCR"""
        
        # First, wait for Battle.net to actually launch
        max_window_attempts = 10  # Try up to 10 times to find Battle.net window
        window_attempt = 0
        
        while window_attempt < max_window_attempts:
            window_attempt += 1
            
            # Check if user stopped the bot
            if not self.bot_running:
                return False
            
            try:
                import pyautogui
                import pygetwindow as gw
                
                # Find Battle.net window - look for the main window (larger one)
                battlenet_windows = gw.getWindowsWithTitle("Battle.net")
                if not battlenet_windows:
                    time.sleep(3)
                    continue
                
                # Find the main Battle.net window (larger one, not the initial small window)
                main_battlenet_window = None
                max_area = 0
                
                for window in battlenet_windows:
                    area = window.width * window.height
                    
                    # Prefer larger windows (main window) over smaller ones (initial window)
                    if area > max_area:
                        max_area = area
                        main_battlenet_window = window
                
                if not main_battlenet_window:
                    time.sleep(3)
                    continue
                
                battlenet_window = main_battlenet_window
                
                # Force focus the window
                battlenet_window.activate()
                time.sleep(1)  # Wait for activation
                
                # Double-check focus by bringing to front
                battlenet_window.minimize()
                time.sleep(0.5)
                battlenet_window.restore()
                time.sleep(0.5)
                battlenet_window.activate()
                time.sleep(2)  # Wait longer for window to be fully active
                
                # Get window position and size
                x, y, width, height = battlenet_window.left, battlenet_window.top, battlenet_window.width, battlenet_window.height
                
                # Validate window dimensions
                if width <= 0 or height <= 0:
                    time.sleep(3)
                    continue
                
                # Check if this is the correct window (width should be larger than height for main window)
                if height > width:
                    time.sleep(3)
                    continue
                
                # Battle.net window found and valid - now start button detection
                break
                
            except Exception as e:
                if window_attempt < max_window_attempts:
                    time.sleep(3)
        
        if window_attempt >= max_window_attempts:
            return False
        
        # Now search for the PLAY button using OCR
        max_button_attempts = 10  # Try up to 10 times to find the button
        button_attempt = 0
        
        while button_attempt < max_button_attempts:
            button_attempt += 1
            
            # Check if user stopped the bot
            if not self.bot_running:
                return False
            
            try:
                # Take screenshot of only the Battle.net window
                try:
                    screenshot = pyautogui.screenshot(region=(x, y, width, height))
                    screenshot_np = np.array(screenshot)
                    screenshot_rgb = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
                    
                except Exception as screenshot_error:
                    try:
                        screenshot = pyautogui.screenshot()
                        screenshot_np = np.array(screenshot)
                        screenshot_rgb = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
                    except Exception as full_screen_error:
                        time.sleep(3)
                        continue
                
                # Save the window screenshot for debugging
                self.save_debug_screenshot(screenshot_rgb, "battlenet_window", False, f"Window size: {width}x{height}", "play_button")
                
                # Use Umi-OCR HTTP service to find "PLAY" text
                import requests
                import base64
                
                try:
                    # Convert image to base64 for Umi-OCR
                    _, buffer = cv2.imencode('.png', screenshot_rgb)
                    image_base64 = base64.b64encode(buffer).decode('utf-8')
                    
                    # Prepare OCR request - use English for PLAY button detection
                    ocr_data = {
                        "base64": image_base64,
                        "options": {
                            "ocr.language": "English",
                            "ocr.maxSideLen": 1024,
                            "tbpu.parser": "multi_para",
                            "data.format": "dict"  # Get full data with positions
                        }
                    }
                    
                    # Send request to Umi-OCR service
                    response = requests.post(
                        "http://127.0.0.1:1224/api/ocr",
                        json=ocr_data,
                        headers={"Content-Type": "application/json"},
                        timeout=30
                    )
                    
                    if response.status_code != 200:
                        time.sleep(3)
                        continue
                    
                    result = response.json()
                    if result.get('code') != 100:
                        time.sleep(3)
                        continue
                    
                    # Get OCR results
                    ocr_results = result.get('data', [])
                    
                    # First, check if "playing now" is already visible (skip to next step)
                    playing_now_found = False
                    for block in ocr_results:
                        text = block.get('text', '').strip().upper()
                        if "PLAYING NOW" in text or "PLAYING" in text:
                            playing_now_found = True
                            break
                    
                    if playing_now_found:
                        return True
                    
                    # Create debug image
                    debug_image = screenshot_rgb.copy()
                    window_height, window_width = screenshot_rgb.shape[:2]
                    
                    # Draw search region (bottom-left area)
                    search_region_x1 = 0
                    search_region_y1 = int(window_height * 0.7)
                    search_region_x2 = int(window_width * 0.4)  # Wider search area
                    search_region_y2 = window_height
                    
                    cv2.rectangle(debug_image, 
                                 (search_region_x1, search_region_y1), 
                                 (search_region_x2, search_region_y2), 
                                 (0, 255, 0), 2)  # Green rectangle for search area
                    
                    # Add label for search area
                    cv2.putText(debug_image, "SEARCH AREA", (search_region_x1, search_region_y1 - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    
                    # Look for "PLAY" text in the search region
                    play_button_found = False
                    play_text_candidates = []
                    
                    for block in ocr_results:
                        text = block.get('text', '').strip()
                        if text.upper() == "PLAY":
                            # Get text position from Umi-OCR box format
                            box = block.get('box', [])
                            if len(box) >= 4:
                                # Umi-OCR box format: [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]
                                x1, y1 = box[0]
                                x2, y2 = box[2]
                                text_x = int(x1)
                                text_y = int(y1)
                                text_w = int(x2 - x1)
                                text_h = int(y2 - y1)
                                
                                # Check if text is in the search region
                                in_search_region = (text_x >= search_region_x1 and 
                                                  text_x + text_w <= search_region_x2 and
                                                  text_y >= search_region_y1 and 
                                                  text_y + text_h <= search_region_y2)
                                
                                if in_search_region:
                                    # Draw rectangle around the text
                                    cv2.rectangle(debug_image, (text_x, text_y), (text_x + text_w, text_y + text_h), (0, 255, 255), 2)
                                    cv2.putText(debug_image, f"PLAY", (text_x, text_y - 5), 
                                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                                    
                                    play_text_candidates.append((text_x, text_y, text_w, text_h))
                    
                    # If we found PLAY text, click on the first candidate
                    if play_text_candidates:
                        best_candidate = play_text_candidates[0]  # Take the first one found
                        text_x, text_y, text_w, text_h = best_candidate
                        
                        # Click on the center of the text
                        click_x = x + text_x + text_w // 2
                        click_y = y + text_y + text_h // 2
                        
                        pyautogui.click(click_x, click_y)
                        
                        # Wait 1 second and verify "launching" or "playing now" is displayed
                        time.sleep(1)
                        
                        # Take another screenshot to verify "launching" or "playing now" is visible
                        try:
                            verify_screenshot = pyautogui.screenshot(region=(x, y, width, height))
                            verify_screenshot_np = np.array(verify_screenshot)
                            verify_screenshot_rgb = cv2.cvtColor(verify_screenshot_np, cv2.COLOR_RGB2BGR)
                            
                            # Use Umi-OCR to check for "launching" or "playing now" text
                            _, verify_buffer = cv2.imencode('.png', verify_screenshot_rgb)
                            verify_image_base64 = base64.b64encode(verify_buffer).decode('utf-8')
                            
                            verify_ocr_data = {
                                "base64": verify_image_base64,
                                "options": {
                                    "ocr.language": "English",
                                    "ocr.maxSideLen": 1024,
                                    "tbpu.parser": "multi_para",
                                    "data.format": "dict"
                                }
                            }
                            
                            verify_response = requests.post(
                                "http://127.0.0.1:1224/api/ocr",
                                json=verify_ocr_data,
                                headers={"Content-Type": "application/json"},
                                timeout=30
                            )
                            
                            if verify_response.status_code == 200:
                                verify_result = verify_response.json()
                                if verify_result.get('code') == 100:
                                    verify_ocr_results = verify_result.get('data', [])
                                    verification_success = False
                                    
                                    for block in verify_ocr_results:
                                        text = block.get('text', '').strip().upper()
                                        if "LAUNCHING" in text or "PLAYING NOW" in text or "PLAYING" in text:
                                            verification_success = True
                                            break
                                    
                                    if not verification_success:
                                        continue  # Retry the button detection
                            
                        except Exception as verify_error:
                            pass
                        
                        # Draw red rectangle on the matched text for success screenshot
                        success_image = screenshot_rgb.copy()
                        cv2.rectangle(success_image, (text_x, text_y), (text_x + text_w, text_y + text_h), (0, 0, 255), 3)
                        cv2.putText(success_image, f"MATCHED PLAY", (text_x, text_y - 10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        
                        # Save success screenshot
                        self.save_debug_screenshot(success_image, "battlenet_ocr_matched", True, 
                                                 f"Matched PLAY text at ({text_x}, {text_y})", "play_button")
                        
                        play_button_found = True
                    
                    # Save debug image with annotations
                    details = f"Umi-OCR found {len(ocr_results)} text blocks, {len(play_text_candidates)} PLAY candidates"
                    self.save_debug_screenshot(debug_image, "battlenet_ocr_search", play_button_found, details, "play_button")
                    
                    if play_button_found:
                        return True
                    else:
                        # If this is not the last attempt, wait before trying again
                        if button_attempt < max_button_attempts:
                            time.sleep(3)
                    
                except Exception as ocr_error:
                    if button_attempt < max_button_attempts:
                        time.sleep(3)
                    
            except Exception as e:
                if button_attempt < max_button_attempts:
                    time.sleep(3)
        
        return False
    
    def _verify_hearthstone_launched(self):
        """Verify that Hearthstone has successfully launched and navigate to collection"""
        self.log_message("Waiting for Hearthstone to launch...")
        
        # Wait for Hearthstone to start
        time.sleep(8)
        
        # Wait additional 20 seconds before starting to look for "点击开始"
        time.sleep(20)
        
        try:
            import pygetwindow as gw
            import pyautogui
            import requests
            import base64
            
            # Look for Hearthstone window - try Chinese name first, then English
            hearthstone_windows = gw.getWindowsWithTitle("炉石传说")
            if not hearthstone_windows:
                # Try English name as fallback
                hearthstone_windows = gw.getWindowsWithTitle("Hearthstone")
                if not hearthstone_windows:
                    self.log_message("Hearthstone window not found (tried both '炉石传说' and 'Hearthstone')")
                    return False
            
            hearthstone_window = hearthstone_windows[0]
            
            # Verify this is not our own GUI window
            if "Control Panel" in hearthstone_window.title or "Bot" in hearthstone_window.title:
                self.log_message("ERROR: Detected our own GUI window instead of Hearthstone game window")
                return False
            
            # Focus the window
            hearthstone_window.activate()
            time.sleep(2)
            
            # Get window position and size
            x, y, width, height = hearthstone_window.left, hearthstone_window.top, hearthstone_window.width, hearthstone_window.height
            
            # Step 1: Look for "点击开始" (Click to Start) at the bottom of the screen
            if not self._find_and_click_text("点击开始", x, y, width, height, "bottom", "click_start"):
                # If "点击开始" not found, check if we're already at home screen (look for "传统对战")
                if self._find_and_click_text("传统对战", x, y, width, height, "anywhere", "home_screen_check", click_if_found=False):
                    self.log_message("Already at home screen (found '传统对战'), skipping '点击开始' step")
                else:
                    self.log_message("Could not find '点击开始' button")
                    return False
            else:
                # Wait for the home screen to load after clicking "点击开始"
                time.sleep(3)
            
            # Step 2: Look for "收藏" (Collection) button
            if not self._find_and_click_text("收藏", x, y, width, height, "anywhere", "collection"):
                self.log_message("Could not find '收藏' button")
                return False
            
            # Wait for collection to load
            time.sleep(2)
            
            # Take a final screenshot to confirm we're in collection
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            screenshot_np = np.array(screenshot)
            screenshot_rgb = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            
            # Save final verification screenshot
            self.save_debug_screenshot(screenshot_rgb, "hearthstone_collection_reached", True, f"Successfully reached collection: {width}x{height}")
            
            self.log_message("SUCCESS: Reached Hearthstone collection!")
            return True
            
        except Exception as e:
            self.log_message(f"Error in Hearthstone navigation: {e}")
            return False
    
    def _find_and_click_text(self, target_text, window_x, window_y, window_width, window_height, search_region="anywhere", attempt_type="text_search", click_if_found=True):
        """Find and click text within the Hearthstone window"""
        import base64  # Import base64 for image encoding
        import requests  # Import requests for Umi-OCR API calls
        import re  # Import re for character extraction
        max_attempts = 10  # Increased from 5 to 10 attempts
        attempt = 0
        
        def extract_chinese_characters(text):
            """Extract all Chinese characters from text"""
            # Unicode range for Chinese characters
            chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
            return chinese_pattern.findall(text)
        

        
        # Ground truth comparison removed as requested by user
        
        while attempt < max_attempts:
            attempt += 1
            
            # Check if user stopped the bot
            if not self.bot_running:
                return False
            
            try:
                import pyautogui
                
                # Take screenshot of the Hearthstone window
                screenshot = pyautogui.screenshot(region=(window_x, window_y, window_width, window_height))
                screenshot_np = np.array(screenshot)
                screenshot_rgb = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
                
                # For Chinese text, use the original image for OCR to avoid preprocessing issues
                if "点击" in target_text or "我的" in target_text:
                    # Use original image for Chinese OCR to avoid preprocessing interference
                    ocr_image = screenshot_rgb
                else:
                    # Apply some image preprocessing to improve OCR accuracy for English text
                    # Convert to grayscale for better text detection
                    gray = cv2.cvtColor(screenshot_rgb, cv2.COLOR_BGR2GRAY)
                    
                    # Apply slight blur to reduce noise
                    blurred = cv2.GaussianBlur(gray, (1, 1), 0)
                    
                    # Apply adaptive thresholding to improve text contrast
                    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
                    
                    # Convert back to BGR for consistency
                    ocr_image = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
                
                # Convert image to base64 for Umi-OCR
                _, buffer = cv2.imencode('.png', ocr_image)
                image_base64 = base64.b64encode(buffer).decode('utf-8')
                
                # Prepare OCR request - try Chinese first for Chinese text, then English as fallback
                if "点击" in target_text or "我的" in target_text:
                    # For Chinese text, try Chinese OCR first
                    ocr_language = "简体中文"
                else:
                    ocr_language = "English"
                
                ocr_data = {
                    "base64": image_base64,
                    "options": {
                        "ocr.language": ocr_language,
                        "ocr.maxSideLen": 1024,
                        "tbpu.parser": "multi_para",
                        "data.format": "dict"
                    }
                }
                
                # Send request to Umi-OCR service
                response = requests.post(
                    "http://127.0.0.1:1224/api/ocr",
                    json=ocr_data,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if response.status_code != 200:
                    time.sleep(2)
                    continue
                
                result = response.json()
                if result.get('code') != 100:
                    # Try with original image if processed image failed
                    if "processed_image" in locals():
                        _, buffer = cv2.imencode('.png', screenshot_rgb)
                        image_base64 = base64.b64encode(buffer).decode('utf-8')
                        ocr_data["base64"] = image_base64
                        
                        response = requests.post(
                            "http://127.0.0.1:1224/api/ocr",
                            json=ocr_data,
                            headers={"Content-Type": "application/json"},
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            if result.get('code') != 100:
                                # Continue to language fallback
                                pass
                        else:
                            # Continue to language fallback
                            pass
                    
                    # If Chinese OCR failed, try English as fallback for Chinese text
                    if ocr_language == "简体中文" and ("点击" in target_text or "我的" in target_text):
                        ocr_data["options"]["ocr.language"] = "English"
                        
                        response = requests.post(
                            "http://127.0.0.1:1224/api/ocr",
                            json=ocr_data,
                            headers={"Content-Type": "application/json"},
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            if result.get('code') != 100:
                                time.sleep(2)
                                continue
                        else:
                            time.sleep(2)
                            continue
                    else:
                        # If OCR failed, wait and try again
                        time.sleep(2)
                        continue
                
                # Get OCR results
                ocr_results = result.get('data', [])
                
                # Create debug image (use original for visualization, processed for OCR)
                debug_image = screenshot_rgb.copy()
                
                # Frame ALL detected text blocks in debug image
                for i, block in enumerate(ocr_results):
                    text = block.get('text', '').strip()
                    box = block.get('box', [])
                    if box and len(box) >= 4:
                        x1, y1 = box[0]
                        x2, y2 = box[2]
                        text_x = int(x1)
                        text_y = int(y1)
                        text_w = int(x2 - x1)
                        text_h = int(y2 - y1)
                        
                        # Draw rectangle around ALL detected text blocks
                        cv2.rectangle(debug_image, (text_x, text_y), (text_x + text_w, text_y + text_h), (128, 128, 128), 1)  # Gray rectangle
                        # Use a font that supports Chinese characters for labels
                        try:
                            cv2.putText(debug_image, f"{i}: {text}", (text_x, text_y - 5), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, (128, 128, 128), 1)
                        except:
                            # Fallback if Chinese characters can't be displayed
                            cv2.putText(debug_image, f"{i}: Text_{i}", (text_x, text_y - 5), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, (128, 128, 128), 1)
                window_height, window_width = screenshot_rgb.shape[:2]
                
                # Define search region based on parameter
                if search_region == "bottom":
                    search_region_x1 = 0
                    search_region_y1 = int(window_height * 0.7)  # Bottom 30%
                    search_region_x2 = window_width
                    search_region_y2 = window_height
                else:  # "anywhere"
                    search_region_x1 = 0
                    search_region_y1 = 0
                    search_region_x2 = window_width
                    search_region_y2 = window_height
                
                # Draw search region
                cv2.rectangle(debug_image, 
                             (search_region_x1, search_region_y1), 
                             (search_region_x2, search_region_y2), 
                             (0, 255, 0), 2)  # Green rectangle
                
                # Add label for search area
                cv2.putText(debug_image, f"SEARCH: {target_text}", (search_region_x1, search_region_y1 - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                
                # Look for target text
                text_found = False
                text_candidates = []
                
                # Special handling for "点击开始" - collect all Chinese characters and check for all 4 characters
                if "点击开始" in target_text:
                    # Add compact logging for 点击开始 detection
                    self.log_message(f"[点击开始] Attempt {attempt}: Found {len(ocr_results)} text blocks")
                    
                    # Collect all Chinese characters from all text blocks with their individual positions
                    all_chinese_chars = set()
                    char_positions = {}  # Store positions of each character
                    
                    for block in ocr_results:
                        text = block.get('text', '').strip()
                        box = block.get('box', [])
                        
                        if box and len(box) >= 4:
                            x1, y1 = box[0]
                            x2, y2 = box[2]
                            text_x = int(x1)
                            text_y = int(y1)
                            text_w = int(x2 - x1)
                            text_h = int(y2 - y1)
                            
                            # Extract Chinese characters from this text block
                            chinese_chars = extract_chinese_characters(text)
                            
                            # Log Chinese characters found in this block
                            if chinese_chars:
                                self.log_message(f"[点击开始] Block '{text}': Found chars {chinese_chars}")
                            
                            # Calculate individual character positions within the text block
                            if chinese_chars:
                                # For Chinese characters, assume they are roughly square and evenly spaced
                                # Calculate character width based on the number of Chinese characters
                                chinese_char_count = len(chinese_chars)
                                if chinese_char_count > 0:
                                    char_width = text_w // chinese_char_count
                                    for i, char in enumerate(chinese_chars):
                                        all_chinese_chars.add(char)
                                        # Calculate position of this character within the text block
                                        char_x = text_x + (i * char_width)
                                        char_w = char_width
                                        char_y = text_y
                                        char_h = text_h
                                        char_positions[char] = (char_x, char_y, char_w, char_h)
                    
                    # Log if no Chinese characters found in any block
                    if not all_chinese_chars:
                        self.log_message(f"[点击开始] WARNING: No Chinese characters found in any text block")
                                        

                    
                    # Check if all 4 characters of "点击开始" are present
                    target_chars = set("点击开始")
                    found_chars = target_chars.intersection(all_chinese_chars)
                    
                    # Log character matching results
                    self.log_message(f"[点击开始] All chars found: {all_chinese_chars}")
                    self.log_message(f"[点击开始] Target chars: {target_chars}")
                    self.log_message(f"[点击开始] Found chars: {found_chars} ({len(found_chars)}/4)")
                    
                    if len(found_chars) == 4:
                        # All 4 characters found! Frame them out in debug image
                        self.log_message(f"[点击开始] SUCCESS: All 4 characters found, proceeding to click")
                        
                        # Frame out each character in the debug image with yellow rectangles
                        for char in found_chars:
                            if char in char_positions:
                                x, y, w, h = char_positions[char]
                                # Draw yellow rectangle around the character
                                cv2.rectangle(debug_image, (x, y), (x + w, y + h), (0, 255, 255), 2)  # Yellow rectangle (BGR)
                                # Use a font that supports Chinese characters
                                try:
                                    # Try to use a font that supports Chinese characters
                                    font = cv2.FONT_HERSHEY_SIMPLEX
                                    cv2.putText(debug_image, char, (x, y - 5), font, 0.5, (0, 255, 255), 1)
                                except:
                                    # Fallback if Chinese characters can't be displayed
                                    cv2.putText(debug_image, f"Char_{ord(char)}", (x, y - 5), 
                                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                        
                        # Find the "点" character's position for clicking
                        if '点' in char_positions:
                            dot_x, dot_y, dot_w, dot_h = char_positions['点']
                            
                            # Check if "点" is in the search region
                            in_search_region = (dot_x >= search_region_x1 and 
                                              dot_x + dot_w <= search_region_x2 and
                                              dot_y >= search_region_y1 and 
                                              dot_y + dot_h <= search_region_y2)
                            
                            if in_search_region:
                                # Click on the "点" character
                                click_x = window_x + dot_x + dot_w // 2
                                click_y = window_y + dot_y + dot_h // 2
                                
                                self.log_message(f"[点击开始] CLICKING: '点' at ({click_x}, {click_y})")
                                pyautogui.click(click_x, click_y)
                                
                                # Draw red rectangle on the "点" character for success screenshot
                                success_image = screenshot_rgb.copy()
                                cv2.rectangle(success_image, (dot_x, dot_y), (dot_x + dot_w, dot_y + dot_h), (0, 0, 255), 3)
                                cv2.putText(success_image, f"CLICKED '点': {target_text}", (dot_x, dot_y - 10), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                                cv2.putText(success_image, "BOT STEPPED", (dot_x, dot_y + dot_h + 20), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                                
                                # Save success screenshot
                                self.save_debug_screenshot(success_image, f"{attempt_type}_matched", True, 
                                                         f"Clicked '点' character in '{target_text}' at ({dot_x}, {dot_y})", "click_to_start")
                                
                                return True
                            else:
                                self.log_message(f"[点击开始] '点' character outside search region: ({dot_x}, {dot_y}) not in ({search_region_x1}, {search_region_y1}, {search_region_x2}, {search_region_y2})")
                        else:
                            self.log_message(f"[点击开始] ERROR: '点' character not found in char_positions")
                    else:
                        # Not all characters found
                        self.log_message(f"[点击开始] FAILED: Only found {len(found_chars)}/4 characters")
                        
                        # Frame out the characters that were found with yellow rectangles
                        for char in found_chars:
                            if char in char_positions:
                                x, y, w, h = char_positions[char]
                                # Draw yellow rectangle around the found character
                                cv2.rectangle(debug_image, (x, y), (x + w, y + h), (0, 255, 255), 2)  # Yellow rectangle (BGR)
                                try:
                                    # Try to use a font that supports Chinese characters
                                    font = cv2.FONT_HERSHEY_SIMPLEX
                                    cv2.putText(debug_image, char, (x, y - 5), font, 0.5, (0, 255, 255), 1)
                                except:
                                    # Fallback if Chinese characters can't be displayed
                                    cv2.putText(debug_image, f"Char_{ord(char)}", (x, y - 5), 
                                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                
                # Regular text matching for other targets
                for block in ocr_results:
                    text = block.get('text', '').strip()
                    # More flexible matching for Chinese text
                    text_matched = False
                    
                    # Direct match
                    if target_text in text or text in target_text:
                        text_matched = True
                    
                    # Additional patterns for "我的收藏" - comprehensive matching for both Chinese and English
                    elif "我的收藏" in target_text:
                        # Try various patterns that might match "我的收藏"
                        patterns = [
                            "我的收藏", "我的", "收藏", 
                            "My Collection", "Collection", "My collection",
                            "MY COLLECTION", "COLLECTION",
                            "my collection", "collection",
                            # Additional variations that might appear
                            "收藏夹", "我的收藏夹", "卡牌收藏", "卡牌",
                            "Collection Tab", "Cards", "My Cards", "Card Collection",
                            "COLLECTION TAB", "CARDS", "MY CARDS", "CARD COLLECTION"
                        ]
                        for pattern in patterns:
                            if pattern in text:
                                text_matched = True
                                break
                    
                    if not text_matched:
                        continue
                    
                    # Get text position from Umi-OCR box format
                    box = block.get('box', [])
                    if len(box) >= 4:
                        # Umi-OCR box format: [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]
                        x1, y1 = box[0]
                        x2, y2 = box[2]
                        text_x = int(x1)
                        text_y = int(y1)
                        text_w = int(x2 - x1)
                        text_h = int(y2 - y1)
                        
                        # Check if text is in the search region
                        in_search_region = (text_x >= search_region_x1 and 
                                          text_x + text_w <= search_region_x2 and
                                          text_y >= search_region_y1 and 
                                          text_y + text_h <= search_region_y2)
                        
                        if in_search_region:
                            # Draw yellow rectangle around the text
                            cv2.rectangle(debug_image, (text_x, text_y), (text_x + text_w, text_y + text_h), (0, 255, 255), 2)  # Yellow rectangle (BGR)
                            # Use a font that supports Chinese characters
                            try:
                                cv2.putText(debug_image, f"FOUND: {target_text}", (text_x, text_y - 5), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                            except:
                                # Fallback if Chinese characters can't be displayed
                                cv2.putText(debug_image, f"FOUND: Target", (text_x, text_y - 5), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                            
                            text_candidates.append((text_x, text_y, text_w, text_h))
                
                # If we found the text, click on the first candidate
                if text_candidates:
                    best_candidate = text_candidates[0]  # Take the first one found
                    text_x, text_y, text_w, text_h = best_candidate
                    
                    # For other text, click on the center of the text
                    click_x = window_x + text_x + text_w // 2
                    click_y = window_y + text_y + text_h // 2
                    
                    if click_if_found:
                        pyautogui.click(click_x, click_y)
                        
                        # Draw red rectangle on the matched text for success screenshot
                        success_image = screenshot_rgb.copy()
                        cv2.rectangle(success_image, (text_x, text_y), (text_x + text_w, text_y + text_h), (0, 0, 255), 3)
                        cv2.putText(success_image, f"CLICKED: {target_text}", (text_x, text_y - 10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        
                        # Save success screenshot
                        self.save_debug_screenshot(success_image, f"{attempt_type}_matched", True, 
                                                 f"Clicked '{target_text}' at ({text_x}, {text_y})", "text_search")
                    
                    text_found = True
                
                # Save debug image with annotations
                subfolder = "click_to_start" if "点击开始" in target_text else "text_search"
                details = f"Umi-OCR found {len(ocr_results)} text blocks, {len(text_candidates)} '{target_text}' candidates"
                self.save_debug_screenshot(debug_image, f"{attempt_type}_search", text_found, details, subfolder)
                
                if text_found:
                    return True
                else:
                    # If this is not the last attempt, wait before trying again
                    if attempt < max_attempts:
                        time.sleep(2)
                
            except Exception as e:
                if attempt < max_attempts:
                    time.sleep(2)
        
        return False
    
    def check_hearthstone_path(self):
        """Check if Battle.net and Hearthstone paths are valid"""
        self.log_message("Checking Battle.net and Hearthstone path configuration...")
        
        try:
            import os
            from config import get_battlenet_path, get_hearthstone_path, ALTERNATIVE_BATTLENET_PATHS, ALTERNATIVE_PATHS
            
            # Check Battle.net path
            battlenet_path = get_battlenet_path()
            if os.path.exists(battlenet_path):
                self.log_message(f"[OK] Battle.net found at: {battlenet_path}")
            else:
                # Check alternative Battle.net paths
                found_battlenet_paths = []
                for path in ALTERNATIVE_BATTLENET_PATHS:
                    if os.path.exists(path):
                        found_battlenet_paths.append(path)
                
                if found_battlenet_paths:
                    self.log_message(f"[WARNING] Battle.net not found at current path, but found alternatives:")
                    for path in found_battlenet_paths:
                        self.log_message(f"  - {path}")
                else:
                    self.log_message(f"[ERROR] Battle.net not found at any known location")
                    messagebox.showerror("Path Check", 
                                       f"Battle.net executable not found at any known location.\n\n"
                                       f"Current path: {battlenet_path}\n\n"
                                       f"Please check if Battle.net is installed and update config.py")
                    return
            
            # Check Hearthstone path
            hearthstone_path = get_hearthstone_path()
            if os.path.exists(hearthstone_path):
                self.log_message(f"[OK] Hearthstone found at: {hearthstone_path}")
                messagebox.showinfo("Path Check", 
                                  f"Battle.net: {battlenet_path}\n\n"
                                  f"Hearthstone: {hearthstone_path}")
            else:
                # Check alternative Hearthstone paths
                found_hearthstone_paths = []
                for path in ALTERNATIVE_PATHS:
                    if os.path.exists(path):
                        found_hearthstone_paths.append(path)
                
                if found_hearthstone_paths:
                    self.log_message(f"[WARNING] Hearthstone not found at current path, but found alternatives:")
                    for path in found_hearthstone_paths:
                        self.log_message(f"  - {path}")
                    
                    # Show dialog with found paths
                    path_list = "\n".join(found_hearthstone_paths)
                    messagebox.showwarning("Path Check", 
                                         f"Battle.net: {battlenet_path}\n\n"
                                         f"Hearthstone not found at:\n{hearthstone_path}\n\n"
                                         f"But found these alternatives:\n{path_list}\n\n"
                                         f"Please update config.py with the correct path.")
                else:
                    self.log_message(f"[ERROR] Hearthstone not found at any known location")
                    messagebox.showerror("Path Check", 
                                       f"Battle.net: {battlenet_path}\n\n"
                                       f"Hearthstone executable not found at any known location.\n\n"
                                       f"Current path: {hearthstone_path}\n\n"
                                       f"Please check if Hearthstone is installed and update config.py")
                
        except Exception as e:
            self.log_message(f"Error checking paths: {e}")
            messagebox.showerror("Path Check Error", f"Error checking paths: {e}")
    
    def detect_window(self):
        """Detect and focus Hearthstone window"""
        self.log_message("Attempting to detect Hearthstone window...")
        
        try:
            # Take a screenshot before detection attempt
            import pyautogui
            screenshot = pyautogui.screenshot()
            screenshot_np = np.array(screenshot)
            screenshot_rgb = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            
            # Save screenshot for debugging
            self.save_debug_screenshot(screenshot_rgb, "hearthstone_window_detection", False, "Before window detection")
            
            if focus_hearthstone_window():
                self.window_status.config(text="Detected", foreground="green")
                self.log_message("Hearthstone window detected and focused!")
                
                # Take another screenshot after successful detection
                screenshot_after = pyautogui.screenshot()
                screenshot_after_np = np.array(screenshot_after)
                screenshot_after_rgb = cv2.cvtColor(screenshot_after_np, cv2.COLOR_RGB2BGR)
                self.save_debug_screenshot(screenshot_after_rgb, "hearthstone_window_detection", True, "After successful window detection")
                
                # Initialize bot components
                self.initialize_components()
                
            else:
                self.window_status.config(text="Not Found", foreground="red")
                self.log_message("Hearthstone window not found. Please start Hearthstone first.")
                
                # Save screenshot for failed detection
                self.save_debug_screenshot(screenshot_rgb, "hearthstone_window_detection", False, "Window detection failed")
                
                messagebox.showwarning("Window Not Found", 
                                     "Hearthstone window not found.\nPlease start Hearthstone and try again.")
                
        except Exception as e:
            self.log_message(f"Error detecting window: {e}")
            self.window_status.config(text="Error", foreground="red")
    
    def initialize_components(self):
        """Initialize bot components"""
        try:
            self.game_analyzer = GameAnalyzer()
            self.ai_engine = AIEngine()
            self.input_controller = InputController()
            self.log_message("Bot components initialized successfully")
        except Exception as e:
            self.log_message(f"Error initializing components: {e}")
    
    def test_components(self):
        """Test all bot components"""
        if not self.game_analyzer:
            messagebox.showwarning("Components Not Ready", 
                                 "Please detect Hearthstone window first.")
            return
        
        self.log_message("Starting component tests...")
        
        # Run tests in a separate thread
        test_thread = threading.Thread(target=self._run_tests)
        test_thread.daemon = True
        test_thread.start()
    
    def _run_tests(self):
        """Run component tests in background thread"""
        try:
            # Test screenshot capture
            self.log_message("Testing screenshot capture...")
            screenshot = get_hearthstone_screenshot()
            if screenshot is not None:
                self.log_message(f"✓ Screenshot capture works (shape: {screenshot.shape})")
                
                # Save test screenshot
                self.save_debug_screenshot(screenshot, "component_test_screenshot", True, f"Screenshot shape: {screenshot.shape}")
                
            else:
                self.log_message("✗ Screenshot capture failed")
                return
            
            # Test game analysis
            self.log_message("Testing game analysis...")
            game_state = self.game_analyzer.analyze_game_state(screenshot)
            self.log_message(f"✓ Game analysis works")
            self.log_message(f"  - Detected {len(game_state.get('hand_cards', []))} cards in hand")
            self.log_message(f"  - Current mana: {game_state.get('mana', {}).get('current_mana', 0)}")
            
            # Test AI decision making
            self.log_message("Testing AI decision making...")
            decision = self.ai_engine.decide_next_move(game_state)
            self.log_message(f"✓ AI decision making works")
            self.log_message(f"  - Decision: {decision.get('action', 'unknown')}")
            
            self.log_message("🎉 All component tests passed!")
            messagebox.showinfo("Tests Complete", "All component tests passed successfully!")
            
        except Exception as e:
            self.log_message(f"✗ Test failed: {e}")
            messagebox.showerror("Test Failed", f"Component test failed: {e}")
    
    def toggle_analysis_mode(self):
        """Toggle analysis mode on/off"""
        if self.running and self.analysis_thread and self.analysis_thread.is_alive():
            self.stop_analysis_mode()
        else:
            self.start_analysis_mode()
    
    def start_analysis_mode(self):
        """Start analysis mode"""
        if not self.game_analyzer:
            messagebox.showwarning("Components Not Ready", 
                                 "Please detect Hearthstone window first.")
            return
        
        self.running = True
        self.analysis_thread = threading.Thread(target=self._run_analysis_mode)
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
        
        self.analysis_btn.config(text="Stop Analysis")
        self.bot_status.config(text="Analyzing", foreground="blue")
        self.mode_status.config(text="Analysis Mode", foreground="blue")
        self.log_message("Analysis mode started")
    
    def stop_analysis_mode(self):
        """Stop analysis mode"""
        self.running = False
        if self.analysis_thread:
            self.analysis_thread.join(timeout=1)
        
        self.analysis_btn.config(text="Start Analysis Mode")
        self.bot_status.config(text="Stopped", foreground="orange")
        self.mode_status.config(text="None", foreground="gray")
        self.log_message("Analysis mode stopped")
    
    def _run_analysis_mode(self):
        """Run analysis mode in background thread"""
        while self.running:
            try:
                # Take screenshot
                screenshot = get_hearthstone_screenshot()
                if screenshot is None:
                    time.sleep(1)
                    continue
                
                # Analyze game state
                game_state = self.game_analyzer.analyze_game_state(screenshot)
                
                # Update GUI with game state
                self.root.after(0, self.update_game_state_display, game_state)
                
                time.sleep(2)
                
            except Exception as e:
                self.log_message(f"Error in analysis mode: {e}")
                time.sleep(1)
    
    def toggle_auto_play(self):
        """Toggle auto-play mode on/off"""
        if self.running and self.auto_play_thread and self.auto_play_thread.is_alive():
            self.stop_auto_play()
        else:
            self.start_auto_play()
    
    def start_auto_play(self):
        """Start auto-play mode"""
        if not self.game_analyzer:
            messagebox.showwarning("Components Not Ready", 
                                 "Please detect Hearthstone window first.")
            return
        
        # Confirm auto-play
        result = messagebox.askyesno("Auto-Play Warning", 
                                   "Auto-play mode will control your mouse and keyboard.\n\n"
                                   "⚠️ Use at your own risk!\n"
                                   "Move mouse to top-left corner to stop.\n\n"
                                   "Do you want to continue?")
        if not result:
            return
        
        self.running = True
        self.auto_play_thread = threading.Thread(target=self._run_auto_play)
        self.auto_play_thread.daemon = True
        self.auto_play_thread.start()
        
        self.autoplay_btn.config(text="Stop Auto-Play")
        self.bot_status.config(text="Auto-Playing", foreground="red")
        self.mode_status.config(text="Auto-Play Mode", foreground="red")
        self.log_message("Auto-play mode started")
    
    def stop_auto_play(self):
        """Stop auto-play mode"""
        self.running = False
        if self.auto_play_thread:
            self.auto_play_thread.join(timeout=1)
        
        self.autoplay_btn.config(text="Start Auto-Play")
        self.bot_status.config(text="Stopped", foreground="orange")
        self.mode_status.config(text="None", foreground="gray")
        self.log_message("Auto-play mode stopped")
    
    def _run_auto_play(self):
        """Run auto-play mode in background thread"""
        while self.running:
            try:
                # Take screenshot
                screenshot = get_hearthstone_screenshot()
                if screenshot is None:
                    time.sleep(1)
                    continue
                
                # Analyze game state
                game_state = self.game_analyzer.analyze_game_state(screenshot)
                
                # Update GUI
                self.root.after(0, self.update_game_state_display, game_state)
                
                # Make decision
                decision = self.ai_engine.decide_next_move(game_state)
                
                # Execute decision
                self._execute_decision(decision, game_state)
                
                time.sleep(1)
                
            except Exception as e:
                self.log_message(f"Error in auto-play mode: {e}")
                time.sleep(1)
    
    def _execute_decision(self, decision, game_state):
        """Execute AI decision"""
        action = decision.get('action', 'wait')
        reason = decision.get('reason', 'No reason given')
        
        self.log_message(f"Executing: {action} - {reason}")
        
        if action == 'wait':
            time.sleep(2)
        elif action == 'end_turn':
            self.input_controller.click_end_turn()
            time.sleep(1)
        elif action == 'play_card':
            # Simplified card playing logic
            card = decision.get('card')
            if card:
                self.log_message(f"Playing card: {card.get('name', 'Unknown')}")
                # Add actual card playing logic here
                time.sleep(2)
    
    def update_game_state_display(self, game_state):
        """Update the game state display"""
        # Clear existing items
        for item in self.game_tree.get_children():
            self.game_tree.delete(item)
        
        # Add game state information
        if game_state:
            # Hand cards
            hand_cards = game_state.get('hand_cards', [])
            self.game_tree.insert("", tk.END, values=("Hand Cards", f"{len(hand_cards)} cards"))
            
            # Board state
            board_state = game_state.get('board_state', {})
            friendly_minions = board_state.get('friendly_minions', [])
            enemy_minions = board_state.get('enemy_minions', [])
            self.game_tree.insert("", tk.END, values=("Friendly Minions", len(friendly_minions)))
            self.game_tree.insert("", tk.END, values=("Enemy Minions", len(enemy_minions)))
            
            # Mana
            mana_info = game_state.get('mana', {})
            current_mana = mana_info.get('current_mana', 0)
            self.game_tree.insert("", tk.END, values=("Current Mana", current_mana))
            
            # Game phase
            game_phase = game_state.get('game_phase', 'unknown')
            self.game_tree.insert("", tk.END, values=("Game Phase", game_phase))
            
            # Turn number
            turn_number = game_state.get('turn_number', 0)
            self.game_tree.insert("", tk.END, values=("Turn Number", turn_number))
        else:
            self.game_tree.insert("", tk.END, values=("Status", "No game data available"))
    
    def log_message(self, message):
        """Add a message to the log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] INFO: {message}"
        self.log_text.insert(tk.END, log_entry + "\n")
        self.log_text.see(tk.END)
        
        # Also write to CLI log file for parallel monitoring
        try:
            import json
            from pathlib import Path
            
            # Create logs directory if it doesn't exist
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            # Write to CLI log file
            cli_log_path = log_dir / "bot_cli.log"
            entry = {
                'timestamp': timestamp,
                'level': 'INFO',
                'message': message
            }
            
            with open(cli_log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            # Don't log the logging error to avoid infinite recursion
            pass
    
    def clear_logs(self):
        """Clear the log display"""
        self.log_text.delete(1.0, tk.END)
    
    def save_logs(self):
        """Save logs to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.log_message(f"Logs saved to {filename}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save logs: {e}")
    
    def cleanup(self):
        """Cleanup resources when closing"""
        try:
            # Stop bot if running
            if self.bot_running:
                self.stop_bot()
            
            # Unregister global hotkeys
            keyboard.unhook_all()
            self.log_message("Global hotkeys unregistered")
        except Exception as e:
            self.log_message(f"Error during cleanup: {e}")


def main():
    """Main entry point for the GUI"""
    root = tk.Tk()
    app = HearthstoneBotGUI(root)
    
    # Handle window close
    def on_closing():
        if app.bot_running:
            if messagebox.askokcancel("Quit", "Bot is still running. Do you want to stop it and quit?"):
                app.cleanup()
                root.destroy()
        else:
            app.cleanup()
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the GUI
    root.mainloop()


if __name__ == "__main__":
    main() 