#!/usr/bin/env python3
"""
CLI Logger for Hearthstone Bot
Provides command-line logging and monitoring capabilities alongside the GUI
"""

import os
import sys
import time
import threading
import json
from datetime import datetime
from pathlib import Path

class CLILogger:
    def __init__(self, log_file="bot_cli.log"):
        self.log_file = log_file
        self.log_lock = threading.Lock()
        self.running = False
        self.log_thread = None
        
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        self.log_path = log_dir / log_file
        
    def start(self):
        """Start the CLI logger"""
        if self.running:
            return
            
        self.running = True
        self.log_thread = threading.Thread(target=self._monitor_logs, daemon=True)
        self.log_thread.start()
        
        print(f"[{self._timestamp()}] CLI Logger started")
        print(f"[{self._timestamp()}] Monitoring bot activity...")
        print(f"[{self._timestamp()}] Log file: {self.log_path}")
        print("-" * 60)
        
    def stop(self):
        """Stop the CLI logger"""
        self.running = False
        if self.log_thread:
            self.log_thread.join(timeout=1)
        print(f"[{self._timestamp()}] CLI Logger stopped")
        
    def _timestamp(self):
        """Get current timestamp"""
        return datetime.now().strftime("%H:%M:%S")
        
    def _monitor_logs(self):
        """Monitor and display log entries"""
        last_position = 0
        
        while self.running:
            try:
                if self.log_path.exists():
                    with open(self.log_path, 'r', encoding='utf-8') as f:
                        f.seek(last_position)
                        new_lines = f.readlines()
                        last_position = f.tell()
                        
                        for line in new_lines:
                            if line.strip():
                                # Parse and display log entry
                                self._display_log_entry(line.strip())
                                
            except Exception as e:
                print(f"[{self._timestamp()}] Error reading log: {e}")
                
            time.sleep(0.1)  # Check every 100ms
            
    def _display_log_entry(self, log_line):
        """Display a formatted log entry"""
        try:
            # Try to parse JSON log entry
            if log_line.startswith('{'):
                entry = json.loads(log_line)
                timestamp = entry.get('timestamp', '')
                level = entry.get('level', 'INFO')
                message = entry.get('message', '')
                
                # Color coding for different log levels
                if level == 'ERROR':
                    print(f"\033[91m[{timestamp}] {level}: {message}\033[0m")  # Red
                elif level == 'WARNING':
                    print(f"\033[93m[{timestamp}] {level}: {message}\033[0m")  # Yellow
                elif level == 'SUCCESS':
                    print(f"\033[92m[{timestamp}] {level}: {message}\033[0m")  # Green
                else:
                    print(f"[{timestamp}] {level}: {message}")
            else:
                # Simple text log entry
                print(log_line)
                
        except json.JSONDecodeError:
            # Fallback to simple text display
            print(log_line)
            
    def log_event(self, level, message):
        """Log an event to the CLI log file"""
        with self.log_lock:
            entry = {
                'timestamp': self._timestamp(),
                'level': level,
                'message': message
            }
            
            try:
                with open(self.log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(entry) + '\n')
            except Exception as e:
                print(f"[{self._timestamp()}] Error writing to log: {e}")
                
    def show_status(self):
        """Show current bot status"""
        print(f"\n[{self._timestamp()}] Bot Status:")
        print("-" * 40)
        
        # Check if bot is running by looking for process
        try:
            import psutil
            bot_running = False
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] == 'python.exe' and any('launcher.py' in arg for arg in proc.info['cmdline'] or []):
                        bot_running = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
            print(f"Bot Process: {'Running' if bot_running else 'Not Running'}")
        except ImportError:
            print("Bot Process: Unknown (psutil not available)")
            
        # Check log file size
        if self.log_path.exists():
            size = self.log_path.stat().st_size
            print(f"Log File Size: {size} bytes")
        else:
            print("Log File: Not found")
            
        # Check recent screenshots
        screenshot_dir = Path("screenshots/image_recognition_attempts")
        if screenshot_dir.exists():
            recent_screenshots = list(screenshot_dir.glob("*.png"))
            print(f"Recent Screenshots: {len(recent_screenshots)} files")
            
            # Show last 3 screenshots
            if recent_screenshots:
                recent_screenshots.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                print("Latest screenshots:")
                for i, screenshot in enumerate(recent_screenshots[:3]):
                    mtime = datetime.fromtimestamp(screenshot.stat().st_mtime)
                    print(f"  {i+1}. {screenshot.name} ({mtime.strftime('%H:%M:%S')})")
        else:
            print("Screenshots: Directory not found")
            
        print("-" * 40)

def main():
    """Main CLI logger interface"""
    logger = CLILogger()
    
    print("Hearthstone Bot CLI Logger")
    print("=" * 40)
    print("Commands:")
    print("  start   - Start monitoring bot activity")
    print("  stop    - Stop monitoring")
    print("  status  - Show current bot status")
    print("  help    - Show this help")
    print("  quit    - Exit CLI logger")
    print("=" * 40)
    print("Type 'start' to begin monitoring bot activity...")
    print("=" * 40)
    
    try:
        while True:
            command = input(f"[{logger._timestamp()}] CLI> ").strip().lower()
            
            if command == 'start':
                logger.start()
            elif command == 'stop':
                logger.stop()
            elif command == 'status':
                logger.show_status()
            elif command == 'help':
                print("Commands: start, stop, status, help, quit")
            elif command == 'quit':
                logger.stop()
                break
            elif command:
                print(f"Unknown command: {command}")
                print("Type 'help' for available commands")
                
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        logger.stop()
    except EOFError:
        print("\nExiting...")
        logger.stop()

if __name__ == "__main__":
    main() 