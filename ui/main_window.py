"""
Main window for the refactored Hearthstone Bot GUI
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import time
from pynput import keyboard
from datetime import datetime
from typing import Dict, Any

from core import BotController, BotState


class MainWindow:
    """Main GUI window for the refactored bot"""
    
    def __init__(self, root: tk.Tk, bot_controller: BotController, services: Dict[str, Any]):
        self.root = root
        self.bot_controller = bot_controller
        self.services = services
        self.logger = services['logger']
        
        # Add button debouncing
        self.last_button_click_time = 0
        self.button_debounce_delay = 1.0  # 1 second debounce
        
        # Setup GUI
        self.setup_window()
        self.setup_gui()
        self.setup_logging()
        
        # Setup global hotkeys
        self.setup_global_hotkeys()
        
        # Start log consumer
        self.consume_logs()
        
        # Start status updater
        self.update_status()
    
    def setup_window(self):
        """Setup the main window"""
        self.root.title("Hearthstone Bot - Refactored Control Panel")
        self.root.geometry("1200x700")
        self.root.resizable(True, True)
    
    def setup_gui(self):
        """Setup the GUI layout"""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, minsize=400)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)  # Changed from 2 to 3 due to debug frame
        
        # Title
        title_label = ttk.Label(main_frame, text="Hearthstone Bot - Refactored Control Panel", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Control buttons
        self.setup_control_buttons(main_frame)
        
        # Status panel
        self.setup_status_panel(main_frame)
        
        # Log panel
        self.setup_log_panel(main_frame)
    
    def setup_control_buttons(self, parent):
        """Setup control buttons"""
        control_frame = ttk.LabelFrame(parent, text="Controls", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Configure button layout for 3 columns
        for i in range(3):
            control_frame.columnconfigure(i, weight=1)
        
        # Start/Stop button
        self.start_btn = ttk.Button(control_frame, text="START", command=self.toggle_bot)
        self.start_btn.grid(row=0, column=0, padx=(0, 5), pady=5, sticky=(tk.W, tk.E))
        
        # Status button
        self.status_btn = ttk.Button(control_frame, text="Check Status", command=self.check_status)
        self.status_btn.grid(row=0, column=1, padx=(0, 5), pady=5, sticky=(tk.W, tk.E))
        
        # Clear logs button
        self.clear_btn = ttk.Button(control_frame, text="Clear Logs", command=self.clear_logs)
        self.clear_btn.grid(row=0, column=2, padx=(0, 5), pady=5, sticky=(tk.W, tk.E))
        
        # Debug utilities frame
        debug_frame = ttk.LabelFrame(parent, text="Debug Utilities", padding="10")
        debug_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Configure debug button layout for 5 columns
        for i in range(5):
            debug_frame.columnconfigure(i, weight=1)
        
        # Debug screenshot buttons
        self.debug_whole_btn = ttk.Button(debug_frame, text="Screenshot Whole", command=self.debug_screenshot_whole)
        self.debug_whole_btn.grid(row=0, column=0, padx=(0, 2), pady=5, sticky=(tk.W, tk.E))
        
        self.debug_left_btn = ttk.Button(debug_frame, text="Screenshot Left", command=self.debug_screenshot_left)
        self.debug_left_btn.grid(row=0, column=1, padx=(0, 2), pady=5, sticky=(tk.W, tk.E))
        
        self.debug_right_btn = ttk.Button(debug_frame, text="Screenshot Right", command=self.debug_screenshot_right)
        self.debug_right_btn.grid(row=0, column=2, padx=(0, 2), pady=5, sticky=(tk.W, tk.E))
        
        self.debug_top_btn = ttk.Button(debug_frame, text="Screenshot Top", command=self.debug_screenshot_top)
        self.debug_top_btn.grid(row=0, column=3, padx=(0, 2), pady=5, sticky=(tk.W, tk.E))
        
        self.debug_bottom_btn = ttk.Button(debug_frame, text="Screenshot Bottom", command=self.debug_screenshot_bottom)
        self.debug_bottom_btn.grid(row=0, column=4, padx=(0, 2), pady=5, sticky=(tk.W, tk.E))
    
    def setup_status_panel(self, parent):
        """Setup status panel"""
        status_frame = ttk.LabelFrame(parent, text="Status", padding="10")
        status_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        # Status indicators
        ttk.Label(status_frame, text="Bot Status:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.bot_status = ttk.Label(status_frame, text="Stopped", foreground="orange", font=("Arial", 9))
        self.bot_status.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(status_frame, text="Current Step:", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.step_status = ttk.Label(status_frame, text="None", foreground="gray", font=("Arial", 9))
        self.step_status.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(status_frame, text="Elapsed Time:", font=("Arial", 9, "bold")).grid(row=2, column=0, sticky=tk.W, pady=2)
        self.time_status = ttk.Label(status_frame, text="0s", foreground="gray", font=("Arial", 9))
        self.time_status.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(status_frame, text="Error:", font=("Arial", 9, "bold")).grid(row=3, column=0, sticky=tk.W, pady=2)
        self.error_status = ttk.Label(status_frame, text="None", foreground="gray", font=("Arial", 9))
        self.error_status.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=2)
    
    def setup_log_panel(self, parent):
        """Setup log panel"""
        log_frame = ttk.LabelFrame(parent, text="Logs", padding="10")
        log_frame.grid(row=0, column=1, rowspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(log_frame, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def setup_logging(self):
        """Setup logging callback"""
        self.logger.add_gui_callback(self.on_log_message)
    
    def on_log_message(self, log_entry):
        """Handle log messages from the logging service"""
        timestamp = log_entry.get('timestamp', '')
        level = log_entry.get('level', 'INFO')
        message = log_entry.get('message', '')
        
        log_line = f"[{timestamp}] {level}: {message}\n"
        
        # Add to GUI in thread-safe way
        self.root.after(0, self.add_log_line, log_line)
    
    def add_log_line(self, log_line):
        """Add a log line to the GUI"""
        self.log_text.insert(tk.END, log_line)
        self.log_text.see(tk.END)
    
    def consume_logs(self):
        """Consume logs from the logging service"""
        try:
            log_queue = self.logger.get_log_queue()
            while True:
                log_entry = log_queue.get_nowait()
                self.on_log_message(log_entry)
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.consume_logs)
    
    def update_status(self):
        """Update status display"""
        try:
            status = self.bot_controller.get_status()
            
            # Update bot status
            if status['running']:
                self.bot_status.config(text="Running", foreground="green")
                self.start_btn.config(text="STOP")
            else:
                self.bot_status.config(text="Stopped", foreground="orange")
                self.start_btn.config(text="START")
            
            # Update step status
            current_step = status.get('current_step', 'None')
            self.step_status.config(text=current_step)
            
            # Update elapsed time
            elapsed = status.get('elapsed_time', 0)
            self.time_status.config(text=f"{elapsed:.1f}s")
            
            # Update error status
            error = status.get('error_message')
            if error:
                self.error_status.config(text=error[:50] + "..." if len(error) > 50 else error, foreground="red")
            else:
                self.error_status.config(text="None", foreground="gray")
            
        except Exception as e:
            self.logger.error(f"Error updating status: {e}")
        
        # Schedule next update
        self.root.after(1000, self.update_status)
    
    def toggle_bot(self):
        """Toggle bot on/off"""
        import time
        
        # Add debouncing to prevent double clicks
        current_time = time.time()
        if current_time - self.last_button_click_time < self.button_debounce_delay:
            self.logger.warning("Button click ignored due to debouncing")
            return
        
        self.last_button_click_time = current_time
        
        if self.bot_controller.is_running():
            self.logger.info("GUI: Stopping bot via button")
            self.bot_controller.stop()
        else:
            self.logger.info("GUI: Starting bot via button")
            self.bot_controller.start()
    
    def check_status(self):
        """Check and display detailed status"""
        status = self.bot_controller.get_status()
        
        status_text = f"""
Bot Status: {status['state']}
Running: {status['running']}
Current Step: {status.get('current_step', 'None')}
Completed Steps: {', '.join(status.get('completed_steps', []))}
Elapsed Time: {status.get('elapsed_time', 0):.1f}s
Retry Count: {status.get('retry_count', 0)}
Error: {status.get('error_message', 'None')}
        """.strip()
        
        messagebox.showinfo("Bot Status", status_text)
    
    def clear_logs(self):
        """Clear the log display"""
        self.log_text.delete(1.0, tk.END)
    
    def debug_screenshot_whole(self):
        """Take screenshot of whole screen and detect text"""
        self._debug_screenshot_region("whole", None)
    
    def debug_screenshot_left(self):
        """Take screenshot of left half of screen and detect text"""
        import pyautogui
        screen_width, screen_height = pyautogui.size()
        region = (0, 0, screen_width // 2, screen_height)
        self._debug_screenshot_region("left", region)
    
    def debug_screenshot_right(self):
        """Take screenshot of right half of screen and detect text"""
        import pyautogui
        screen_width, screen_height = pyautogui.size()
        region = (screen_width // 2, 0, screen_width // 2, screen_height)
        self._debug_screenshot_region("right", region)
    
    def debug_screenshot_top(self):
        """Take screenshot of top half of screen and detect text"""
        import pyautogui
        screen_width, screen_height = pyautogui.size()
        region = (0, 0, screen_width, screen_height // 2)
        self._debug_screenshot_region("top", region)
    
    def debug_screenshot_bottom(self):
        """Take screenshot of bottom half of screen and detect text"""
        import pyautogui
        screen_width, screen_height = pyautogui.size()
        region = (0, screen_height // 2, screen_width, screen_height // 2)
        self._debug_screenshot_region("bottom", region)
    
    def _debug_screenshot_region(self, region_name, region):
        """Take screenshot of specified region and detect text"""
        try:
            import pyautogui
            from datetime import datetime
            import os
            
            # Get services
            screenshot_service = self.services.get('screenshot')
            ocr_service = self.services.get('ocr')
            
            if not screenshot_service or not ocr_service:
                self.logger.error("Screenshot or OCR service not available")
                return
            
            # Take screenshot
            if region:
                self.logger.info(f"Taking screenshot of {region_name} region: {region}")
                screenshot = screenshot_service.capture_screen(region=region)
            else:
                self.logger.info(f"Taking screenshot of whole screen")
                screenshot = screenshot_service.capture_screen()
            
            if screenshot is None:
                self.logger.error("Failed to capture screenshot")
                return
            
            # Save screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"debug_{region_name}_{timestamp}.png"
            
            # Create debug directory if it doesn't exist
            debug_dir = "logs/screenshots/debug"
            os.makedirs(debug_dir, exist_ok=True)
            
            filepath = os.path.join(debug_dir, filename)
            screenshot_service.save_screenshot(screenshot, filepath)
            self.logger.info(f"Debug screenshot saved: {filepath}")
            
            # Detect text using OCR
            self.logger.info(f"Detecting text in {region_name} region...")
            text_results = ocr_service.detect_text(screenshot)
            
            if text_results:
                # Filter and categorize detected text
                chinese_text = []
                numbers = []
                symbols = []
                other_text = []
                
                for result in text_results:
                    text = result.get('text', '').strip()
                    if not text:
                        continue
                    
                    # Categorize text
                    has_chinese = any('\u4e00' <= char <= '\u9fff' for char in text)
                    has_numbers = any(char.isdigit() for char in text)
                    has_symbols = any(not char.isalnum() and not char.isspace() and '\u4e00' <= char <= '\u9fff' for char in text)
                    
                    if has_chinese:
                        chinese_text.append(text)
                    elif has_numbers:
                        numbers.append(text)
                    elif has_symbols:
                        symbols.append(text)
                    else:
                        other_text.append(text)
                
                # Log results
                self.logger.info(f"=== TEXT DETECTION RESULTS FOR {region_name.upper()} REGION ===")
                self.logger.info(f"Total text elements detected: {len(text_results)}")
                
                if chinese_text:
                    self.logger.info(f"Chinese text ({len(chinese_text)}): {chinese_text}")
                else:
                    self.logger.info("No Chinese text detected")
                
                if numbers:
                    self.logger.info(f"Numbers ({len(numbers)}): {numbers}")
                else:
                    self.logger.info("No numbers detected")
                
                if symbols:
                    self.logger.info(f"Symbols ({len(symbols)}): {symbols}")
                else:
                    self.logger.info("No symbols detected")
                
                if other_text:
                    self.logger.info(f"Other text ({len(other_text)}): {other_text}")
                else:
                    self.logger.info("No other text detected")
                
                self.logger.info("=== END TEXT DETECTION RESULTS ===")
                
            else:
                self.logger.warning(f"No text detected in {region_name} region")
                
        except Exception as e:
            self.logger.error(f"Error in debug screenshot {region_name}: {e}")
            import traceback
            self.logger.error(f"Stack trace: {traceback.format_exc()}")
    
    def setup_global_hotkeys(self):
        """Setup global hotkeys for F10 (start) and F12 (stop)"""
        try:
            # Create keyboard listener
            self.keyboard_listener = keyboard.GlobalHotKeys({
                '<f10>': self.start_bot_hotkey,
                '<f12>': self.stop_bot_hotkey
            })
            
            # Start listening in a separate thread
            self.keyboard_thread = threading.Thread(target=self.keyboard_listener.start, daemon=True, name="KeyboardListenerThread")
            self.keyboard_thread.start()
            
            self.logger.info(f"Global hotkeys enabled: F10 (Start), F12 (Stop) - Thread ID: {self.keyboard_thread.ident}")
            
        except Exception as e:
            self.logger.error(f"Failed to setup global hotkeys: {e}")
    
    def start_bot_hotkey(self):
        """Handle F10 hotkey to start bot"""
        try:
            self.logger.info("F10 pressed - Starting bot")
            if not self.bot_controller.is_running():
                # Use after() to ensure thread safety
                self.root.after(0, self.bot_controller.start)
            else:
                self.logger.info("F10 pressed - Bot is already running")
        except Exception as e:
            self.logger.error(f"Error in start hotkey: {e}")
    
    def stop_bot_hotkey(self):
        """Handle F12 hotkey to stop bot"""
        try:
            if self.bot_controller.is_running():
                self.logger.info("F12 pressed - Stopping bot")
                # Use after() to ensure thread safety
                self.root.after(0, self.bot_controller.stop)
            else:
                self.logger.info("F12 pressed - Bot is already stopped")
        except Exception as e:
            self.logger.error(f"Error in stop hotkey: {e}")
    
    def cleanup(self):
        """Cleanup resources when window is closed"""
        try:
            self.logger.info("=== CLEANUP START ===")
            
            # Stop the bot if it's running first
            if self.bot_controller.is_running():
                self.logger.info("Stopping bot during cleanup")
                self.bot_controller.stop()
            
            # Stop the keyboard listener
            if hasattr(self, 'keyboard_listener'):
                try:
                    self.logger.info(f"Stopping keyboard listener...")
                    self.keyboard_listener.stop()
                    self.logger.info("Keyboard listener stopped")
                except Exception as e:
                    self.logger.error(f"Error stopping keyboard listener: {e}")
            
            # Force terminate keyboard thread if it's still alive
            if hasattr(self, 'keyboard_thread') and self.keyboard_thread.is_alive():
                try:
                    self.logger.info(f"Keyboard thread still alive (ID: {self.keyboard_thread.ident}), attempting to join...")
                    self.keyboard_thread.join(timeout=1)
                    if self.keyboard_thread.is_alive():
                        self.logger.warning(f"Keyboard thread did not stop (ID: {self.keyboard_thread.ident}), forcing termination")
                        # Force terminate by setting daemon and letting it die
                        self.keyboard_thread.daemon = True
                        # Try to force kill the thread using a more aggressive approach
                        import ctypes
                        try:
                            thread_id = self.keyboard_thread.ident
                            if thread_id:
                                self.logger.info(f"Attempting to terminate thread {thread_id} using ctypes...")
                                res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id), ctypes.py_object(SystemExit))
                                if res > 1:
                                    ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
                                    self.logger.warning("Thread termination failed")
                                else:
                                    self.logger.info("Thread termination signal sent")
                        except Exception as e:
                            self.logger.error(f"Error terminating thread: {e}")
                    else:
                        self.logger.info("Keyboard thread joined successfully")
                except Exception as e:
                    self.logger.error(f"Error joining keyboard thread: {e}")
            
            # Cancel any pending GUI updates
            try:
                self.logger.info("Cancelling pending GUI updates...")
                self.root.after_cancel("all")
                self.logger.info("GUI updates cancelled")
            except:
                self.logger.warning("Could not cancel GUI updates")
            
            # List all active threads for debugging
            import threading
            active_threads = threading.enumerate()
            self.logger.info(f"Active threads at cleanup: {len(active_threads)}")
            for i, thread in enumerate(active_threads):
                self.logger.info(f"  Thread {i+1}: {thread.name} (ID: {thread.ident}, Daemon: {thread.daemon}, Alive: {thread.is_alive()})")
            
            self.logger.info("=== CLEANUP COMPLETE ===")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}") 