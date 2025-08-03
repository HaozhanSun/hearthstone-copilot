"""
Collection Access Step for the Hearthstone Bot
"""

import time
from typing import Dict, Any, Optional, Tuple
from core.bot_state import BotState, BotContext
from core.exceptions import StepException
from .base_step import BaseStep


class CollectionAccessStep(BaseStep):
    """Step to access the Hearthstone collection"""
    
    def get_step_name(self) -> str:
        return "Collection Access"
    
    def can_skip(self, context: BotContext) -> bool:
        # Can skip if we're already in collection
        window_service = self.services.get('window')
        if not window_service:
            return False
        
        hearthstone_window = window_service.find_hearthstone_window()
        if not hearthstone_window:
            return False
        
        return self._check_in_collection(hearthstone_window)
    
    def execute(self, context: BotContext) -> BotContext:
        """Access the Hearthstone collection"""
        try:
            window_service = self.services.get('window')
            screenshot_service = self.services.get('screenshot')
            ocr_service = self.services.get('ocr')
            
            if not all([window_service, screenshot_service, ocr_service]):
                raise StepException(self.get_step_name(), "Required services not available")
            
            # Find Hearthstone window
            hearthstone_window = window_service.find_hearthstone_window()
            if not hearthstone_window:
                raise StepException(self.get_step_name(), "Hearthstone window not found")
            
            # Focus the window
            if not window_service.focus_window(hearthstone_window):
                raise StepException(self.get_step_name(), "Failed to focus Hearthstone window")
            
            # Get window region
            x, y, width, height = window_service.get_window_region(hearthstone_window)
            
            # Check if already in collection
            if self._check_in_collection(hearthstone_window):
                self.logger.info("Already in collection")
                context.update_state(BotState.COMPLETED)
                return context
            
            # Look for "收藏" button
            if self._find_and_click_collection_button(hearthstone_window, window_service, screenshot_service, ocr_service):
                self.logger.info("Clicked '收藏' button")
                time.sleep(2)  # Wait for collection to load
                
                # Take final screenshot to confirm we're in collection
                screenshot = screenshot_service.capture_window_object(hearthstone_window)
                if screenshot is not None:
                    logger = self.services.get('logger')
                    if logger:
                        logger.save_debug_screenshot(
                            screenshot, "hearthstone_collection_reached", True, 
                            f"Successfully reached collection: {width}x{height}"
                        )
                
                self.logger.info("SUCCESS: Reached Hearthstone collection!")
                context.update_state(BotState.COMPLETED)
                return context
            else:
                raise StepException(self.get_step_name(), "Could not find '收藏' button")
            
        except Exception as e:
            if isinstance(e, StepException):
                raise e
            raise StepException(self.get_step_name(), str(e))
    
    def _check_in_collection(self, window) -> bool:
        """Check if we're already in the collection"""
        screenshot_service = self.services.get('screenshot')
        ocr_service = self.services.get('ocr')
        
        if not all([screenshot_service, ocr_service]):
            return False
        
        screenshot = screenshot_service.capture_window_object(window)
        if screenshot is None:
            return False
        
        try:
            # Check for collection-related text
            ocr_results = ocr_service.detect_text(screenshot, "简体中文")
            for block in ocr_results:
                text = block.get('text', '').strip()
                if any(keyword in text for keyword in ["收藏", "卡牌", "我的收藏"]):
                    return True
            
            # Also check English
            ocr_results_en = ocr_service.detect_text(screenshot, "English")
            for block in ocr_results_en:
                text = block.get('text', '').strip().upper()
                if any(keyword in text for keyword in ["COLLECTION", "CARDS", "MY COLLECTION"]):
                    return True
            
            return False
        except Exception:
            return False
    
    def _find_and_click_collection_button(self, window, window_service, screenshot_service, ocr_service) -> bool:
        """Find and click the collection button"""
        try:
            x, y, width, height = window_service.get_window_region(window)
            
            # Take screenshot
            screenshot = screenshot_service.capture_window(x, y, width, height)
            if screenshot is None:
                return False
            
            # Look for "收藏" text anywhere in the window
            coords = ocr_service.find_text_in_region(screenshot, "收藏", (0, 0, width, height), "简体中文")
            if coords:
                center_x = coords[0] + coords[2] // 2
                center_y = coords[1] + coords[3] // 2
                return window_service.click_in_window(window, center_x, center_y)
            
            # Try English "Collection" as fallback
            coords = ocr_service.find_text_in_region(screenshot, "Collection", (0, 0, width, height), "English")
            if coords:
                center_x = coords[0] + coords[2] // 2
                center_y = coords[1] + coords[3] // 2
                return window_service.click_in_window(window, center_x, center_y)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error finding collection button: {e}")
            return False 