"""
OCR Management Step for the Hearthstone Bot
"""

import subprocess
import os
import time
import psutil
import requests
from typing import Dict, Any
from core.bot_state import BotState, BotContext
from .base_step import BaseStep


class OCRManagementStep(BaseStep):
    """Step to manage Umi-OCR service"""
    
    def get_step_name(self) -> str:
        return "OCR Management"
    
    def can_skip(self, context: BotContext) -> bool:
        # Can skip if OCR is already running
        ocr_service = self.services.get('ocr')
        if ocr_service and ocr_service.check_service_status():
            return True
        return False
    
    def execute(self, context: BotContext) -> BotContext:
        """Manage Umi-OCR service"""
        try:
            # Check if Umi-OCR HTTP service is responding
            ocr_service = self.services.get('ocr')
            if ocr_service and ocr_service.check_service_status():
                self.logger.info("Umi-OCR service is already running")
                context.update_state(BotState.LAUNCHING_BATTLENET)
                return context
            
            # Check if Umi-OCR process is running
            umi_ocr_running = False
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    if proc.info['exe'] and 'Umi-OCR' in proc.info['exe']:
                        umi_ocr_running = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if umi_ocr_running:
                self.logger.info("Umi-OCR process found, waiting for service to start")
                # Wait for service to become available
                for _ in range(10):  # Wait up to 10 seconds
                    if ocr_service and ocr_service.check_service_status():
                        self.logger.info("Umi-OCR service is now responding")
                        context.update_state(BotState.LAUNCHING_BATTLENET)
                        return context
                    time.sleep(1)
            
            # Launch Umi-OCR if not running
            ocr_path = "Umi-OCR/Umi-OCR_Rapid_v2.1.5/UmiOCR-data/RUN_GUI.bat"
            if os.path.exists(ocr_path):
                self.logger.info("Launching Umi-OCR...")
                subprocess.Popen([ocr_path], shell=True)
                time.sleep(3)  # Give it time to start
                
                # Wait for service to become available
                for _ in range(15):  # Wait up to 15 seconds
                    if ocr_service and ocr_service.check_service_status():
                        self.logger.info("Umi-OCR service is now running")
                        context.update_state(BotState.LAUNCHING_BATTLENET)
                        return context
                    time.sleep(1)
                
                self.logger.warning("Umi-OCR launched but service not responding")
                context.update_state(BotState.LAUNCHING_BATTLENET)  # Continue anyway
                return context
            else:
                self.logger.error("Umi-OCR not found at expected path")
                context.update_state(BotState.LAUNCHING_BATTLENET)  # Continue anyway
                return context
                
        except Exception as e:
            self.logger.error(f"Error managing OCR: {e}")
            context.update_state(BotState.LAUNCHING_BATTLENET)  # Continue anyway
            return context 