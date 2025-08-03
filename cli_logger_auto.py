#!/usr/bin/env python3
"""
Auto CLI Logger for Hearthstone Bot
Automatically starts monitoring bot activity when launched
"""

import os
import sys
import time
import threading
import json
from datetime import datetime
from pathlib import Path

class AutoCLILogger:
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
        
        print(f"[{self._timestamp()}] Auto CLI Logger started")
        print(f"[{self._timestamp()}] Monitoring bot activity...")
        print(f"[{self._timestamp()}] Log file: {self.log_path}")
        print(f"[{self._timestamp()}] Press Ctrl+C to stop monitoring")
        print("-" * 60)
        
    def stop(self):
        """Stop the CLI logger"""
        self.running = False
        if self.log_thread:
            self.log_thread.join(timeout=1)
        print(f"\n[{self._timestamp()}] Auto CLI Logger stopped")
        
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

def main():
    """Main auto CLI logger interface"""
    logger = AutoCLILogger()
    
    print("Hearthstone Bot Auto CLI Logger")
    print("=" * 50)
    print("This logger automatically starts monitoring bot activity.")
    print("It will display all bot logs in real-time.")
    print("=" * 50)
    
    try:
        # Automatically start monitoring
        logger.start()
        
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nInterrupted by user (Ctrl+C)")
        logger.stop()
    except EOFError:
        print("\nExiting...")
        logger.stop()

if __name__ == "__main__":
    main() 