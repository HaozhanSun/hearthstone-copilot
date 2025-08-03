"""
Hearthstone Navigation Step for the Hearthstone Bot
"""

import time
from typing import Dict, Any, Optional, Tuple
from core.bot_state import BotState, BotContext
from core.exceptions import StepException
from .base_step import BaseStep


class HearthstoneNavigationStep(BaseStep):
    """Step to navigate Hearthstone to the home screen"""
    
    def get_step_name(self) -> str:
        return "Hearthstone Navigation"
    
    def can_skip(self, context: BotContext) -> bool:
        # Can skip if we're already at home screen
        window_service = self.services.get('window')
        if not window_service:
            return False
        
        hearthstone_window = window_service.find_hearthstone_window()
        if not hearthstone_window:
            return False
        
        return self._check_home_screen(hearthstone_window)
    
    def execute(self, context: BotContext) -> BotContext:
        """Navigate Hearthstone to home screen"""
        try:
            # Validate services
            self.validate_services(['window', 'screenshot', 'ocr'])
            window_service = self.get_service('window')
            screenshot_service = self.get_service('screenshot')
            ocr_service = self.get_service('ocr')
            
            # Wait for Hearthstone to launch
            self.logger.info("Waiting for Hearthstone to launch...")
            time.sleep(8)
            
            # Wait additional time before looking for navigation elements
            time.sleep(20)
            
            # Find Hearthstone window
            hearthstone_window = window_service.find_hearthstone_window()
            if not hearthstone_window:
                raise StepException(self.get_step_name(), "Hearthstone window not found")
            
            # Focus the window with retry logic
            if not self.focus_window_with_retry(hearthstone_window, window_service):
                raise StepException(self.get_step_name(), "Failed to focus Hearthstone window")
            
            # Get window region
            x, y, width, height = window_service.get_window_region(hearthstone_window)
            
            # Check if already at home screen
            if self._check_home_screen(hearthstone_window):
                self.logger.info("Already at home screen")
                context.update_state(BotState.ACCESSING_COLLECTION)
                return context
            
            # Look for "点击开始" button
            if self._find_and_click_text(hearthstone_window, "点击开始", "bottom", window_service, screenshot_service, ocr_service):
                self.logger.info("Clicked '点击开始' button")
                time.sleep(3)  # Wait for home screen to load
                context.update_state(BotState.ACCESSING_COLLECTION)
                return context
            else:
                raise StepException(self.get_step_name(), "Could not find '点击开始' button")
            
        except Exception as e:
            if isinstance(e, StepException):
                raise e
            raise StepException(self.get_step_name(), str(e))
    
    def _check_home_screen(self, window) -> bool:
        """Check if we're already at the home screen"""
        screenshot_service = self.get_service('screenshot')
        ocr_service = self.get_service('ocr')
        
        if not all([screenshot_service, ocr_service]):
            return False
        
        screenshot = self.capture_window_screenshot_safe(screenshot_service, window)
        if screenshot is None:
            return False
        
        try:
            ocr_results = ocr_service.detect_text(screenshot, "简体中文")
            for block in ocr_results:
                text = block.get('text', '').strip()
                if "传统对战" in text:
                    return True
            return False
        except Exception:
            return False
    
    def _find_and_click_text(self, window, target_text: str, search_region: str, 
                            window_service, screenshot_service, ocr_service) -> bool:
        """Find and click text in Hearthstone window"""
        try:
            x, y, width, height = window_service.get_window_region(window)
            
            # Take screenshot safely
            screenshot = self.capture_screenshot_safe(screenshot_service, x, y, width, height)
            if screenshot is None:
                return False
            
            # Define search region
            if search_region == "bottom":
                search_region_coords = (0, int(height * 0.7), width, height)
            else:  # "anywhere"
                search_region_coords = (0, 0, width, height)
            
            # Special handling for "点击开始" - find individual characters
            if "点击开始" in target_text:
                return self._find_and_click_chinese_chars(screenshot, target_text, search_region_coords, 
                                                        window, window_service, ocr_service)
            else:
                # Regular text search
                coords = ocr_service.find_text_in_region(screenshot, target_text, search_region_coords)
                if coords:
                    center_x = coords[0] + coords[2] // 2
                    center_y = coords[1] + coords[3] // 2
                    return window_service.click_in_window(window, center_x, center_y)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error finding and clicking text: {e}")
            return False
    
    def _find_and_click_chinese_chars(self, screenshot, target_text: str, search_region: Tuple[int, int, int, int],
                                     window, window_service, ocr_service) -> bool:
        """Find and click Chinese characters for '点击开始'"""
        try:
            target_chars = set("点击开始")
            char_positions = ocr_service.find_chinese_characters(screenshot, target_chars, search_region)
            
            # Check if all 4 characters are found
            if len(char_positions) == 4:
                # Click on the '点' character
                if '点' in char_positions:
                    dot_x, dot_y, dot_w, dot_h = char_positions['点']
                    center_x = dot_x + dot_w // 2
                    center_y = dot_y + dot_h // 2
                    return window_service.click_in_window(window, center_x, center_y)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error finding Chinese characters: {e}")
            return False 