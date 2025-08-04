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
        # Can skip if we're already in collection (specifically "我的收藏")
        window_service = self.services.get('window')
        if not window_service:
            return False
        
        hearthstone_window = window_service.find_hearthstone_window()
        if not hearthstone_window:
            return False
        
        # Only skip if we're actually in "我的收藏" (My Collection), not just any collection-related text
        return self._check_in_collection(hearthstone_window)
    
    def execute(self, context: BotContext) -> BotContext:
        """Access the Hearthstone collection"""
        try:
            # Validate services
            self.validate_services(['window', 'screenshot', 'ocr'])
            window_service = self.get_service('window')
            screenshot_service = self.get_service('screenshot')
            ocr_service = self.get_service('ocr')
            
            # Find Hearthstone window
            hearthstone_window = window_service.find_hearthstone_window()
            if not hearthstone_window:
                raise StepException(self.get_step_name(), "Hearthstone window not found")
            
            # Focus the window with retry logic
            if not self.focus_window_with_retry(hearthstone_window, window_service):
                raise StepException(self.get_step_name(), "Failed to focus Hearthstone window")
            
            # Get window region
            x, y, width, height = window_service.get_window_region(hearthstone_window)
            
            # Wait 8 seconds after clicking "点击开始" before looking for "我的收藏"
            self.logger.info("Waiting 8 seconds after clicking '点击开始' before looking for '我的收藏'...")
            time.sleep(8)
            
            # Check if already in collection
            if self._check_in_collection(hearthstone_window):
                self.logger.info("Already in collection")
                context.update_state(BotState.COMPLETED)
                return context
            
            # Look for "我的收藏" button with detailed debugging
            if self._find_and_click_collection_button(hearthstone_window, window_service, screenshot_service, ocr_service):
                self.logger.info("Clicked '我的收藏' button")
                
                # Wait 3 seconds and verify we're in collection by looking for "我的套牌" in top-right quarter
                self.logger.info("Waiting 3 seconds and verifying we're in collection...")
                time.sleep(3)
                
                # Retry up to 5 times every 2 seconds to find "我的套牌"
                max_retries = 5
                for attempt in range(max_retries):
                    if self._check_in_collection(hearthstone_window):
                        self.logger.info("SUCCESS: Confirmed we're in collection - found '我的套牌'")
                        
                        # Take final screenshot to confirm we're in collection
                        screenshot = self.capture_window_screenshot_safe(screenshot_service, hearthstone_window)
                        if screenshot is not None:
                            self.save_debug_screenshot(screenshot, "hearthstone_collection_reached", True, 
                                                     f"Successfully reached collection: {width}x{height}", "collection")
                        
                        context.update_state(BotState.COMPLETED)
                        return context
                    
                    if attempt < max_retries - 1:
                        self.logger.info(f"Collection verification attempt {attempt + 1}/{max_retries} failed, retrying in 2 seconds...")
                        time.sleep(2)
                
                raise StepException(self.get_step_name(), "Clicked '我的收藏' but could not verify we're in collection after 5 attempts")
            else:
                raise StepException(self.get_step_name(), "Could not find '我的收藏' button")
            
        except Exception as e:
            if isinstance(e, StepException):
                raise e
            raise StepException(self.get_step_name(), str(e))
    
    def _check_in_collection(self, window) -> bool:
        """Check if we're already in the collection by looking for '我的套牌' in top-right quarter"""
        screenshot_service = self.get_service('screenshot')
        ocr_service = self.get_service('ocr')
        window_service = self.get_service('window')
        
        if not all([screenshot_service, ocr_service, window_service]):
            return False
        
        screenshot = self.capture_window_screenshot_safe(screenshot_service, window)
        if screenshot is None:
            return False
        
        # Save debug screenshot for collection verification
        self.save_debug_screenshot(screenshot, "hearthstone_collection_verification", False, 
                                 "Verifying we're in collection", "collection")
        
        try:
            # Get window dimensions
            x, y, width, height = window_service.get_window_region(window)
            
            # Look for "我的套牌" anywhere in the window using detect_text
            ocr_results = ocr_service.detect_text(screenshot, "简体中文")
            if ocr_results:
                self.logger.info("=== COLLECTION VERIFICATION DEBUG ===")
                self.logger.info(f"Window size: {width}x{height}")
                self.logger.info("All detected Chinese text:")
                
                for block in ocr_results:
                    text = block.get('text', '').strip()
                    self.logger.info(f"  - '{text}'")
                    
                    if text == "我的套牌":  # Exact match
                        box = block.get('box', [])
                        if box and len(box) >= 4:
                            x1, y1 = box[0]
                            x2, y2 = box[2]
                            text_x = int(float(x1))
                            text_y = int(float(y1))
                            
                            self.logger.info(f"FOUND '我的套牌' at coordinates: ({text_x}, {text_y})")
                            self.logger.info(f"Already in collection - found '我的套牌' at ({text_x}, {text_y})")
                            return True
                
                self.logger.info("=== END COLLECTION VERIFICATION DEBUG ===")
            
            return False
        except Exception as e:
            self.logger.error(f"Error checking if in collection: {e}")
            return False
    
    def _find_and_click_collection_button(self, window, window_service, screenshot_service, ocr_service) -> bool:
        """Find and click the collection button"""
        try:
            x, y, width, height = window_service.get_window_region(window)
            
            # Take screenshot safely
            screenshot = self.capture_screenshot_safe(screenshot_service, x, y, width, height)
            if screenshot is None:
                return False
            
            # Save debug screenshot in collection subfolder
            self.save_debug_screenshot(screenshot, "hearthstone_collection_search", False, 
                                     f"Searching for '我的收藏' phrase: {width}x{height}", "collection")
            
            # Get all text from the screenshot for debugging
            self.logger.info("=== COLLECTION SEARCH DEBUG ===")
            self.logger.info(f"Window size: {width}x{height}")
            
            # Look for "我的收藏" as a complete phrase using detect_text results
            self.logger.info("Searching for complete phrase '我的收藏' using detect_text results...")
            
            # Get all Chinese text and look for "我的收藏" in the results
            ocr_results = ocr_service.detect_text(screenshot, "简体中文")
            my_collection_coords = None
            
            if ocr_results:
                for block in ocr_results:
                    text = block.get('text', '').strip()
                    if text == "我的收藏":  # Exact match
                        box = block.get('box', [])
                        if box and len(box) >= 4:
                            x1, y1 = box[0]
                            x2, y2 = box[2]
                            # Ensure we're working with scalar values
                            text_x = int(float(x1))
                            text_y = int(float(y1))
                            text_w = int(float(x2) - float(x1))
                            text_h = int(float(y2) - float(y1))
                            
                            my_collection_coords = (text_x, text_y, text_w, text_h)
                            self.logger.info(f"FOUND '我的收藏' at coordinates: ({text_x}, {text_y}) - ({text_x + text_w}, {text_y + text_h})")
                            break
            
            if my_collection_coords:
                center_x = my_collection_coords[0] + my_collection_coords[2] // 2
                center_y = my_collection_coords[1] + my_collection_coords[3] // 2
                self.logger.info(f"Clicking '我的收藏' at center coordinates: ({center_x}, {center_y})")
                
                # Save debug screenshot with found text highlighted
                self.save_debug_screenshot(screenshot, "hearthstone_collection_found", True, 
                                         f"Found '我的收藏' at ({center_x}, {center_y})", "collection")
                
                return window_service.click_in_window(window, center_x, center_y)
            
            # If not found, show all text found on screen for debugging
            self.logger.info("'我的收藏' phrase not found. Showing all text detected on screen:")
            
            # Specifically check for "你的收藏" to see if that's what's being detected
            your_collection_found = False
            for block in ocr_results:
                text = block.get('text', '').strip()
                if text == "你的收藏":  # Exact match
                    box = block.get('box', [])
                    if box and len(box) >= 4:
                        x1, y1 = box[0]
                        x2, y2 = box[2]
                        text_x = int(float(x1))
                        text_y = int(float(y1))
                        self.logger.warning(f"FOUND '你的收藏' at coordinates: ({text_x}, {text_y}) - NOT clicking this!")
                        your_collection_found = True
                        break
            
            # Get all Chinese text
            ocr_results = ocr_service.detect_text(screenshot, "简体中文")
            if ocr_results:
                self.logger.info("Chinese text found:")
                for i, block in enumerate(ocr_results):
                    text = block.get('text', '').strip()
                    box = block.get('box', [])
                    if box and len(box) >= 4:
                        x1, y1 = box[0]
                        x2, y2 = box[2]
                        self.logger.info(f"  [{i+1}] '{text}' at ({int(x1)}, {int(y1)}) - ({int(x2)}, {int(y2)})")
                    else:
                        self.logger.info(f"  [{i+1}] '{text}' (no coordinates)")
            else:
                self.logger.info("No Chinese text found")
            
            # Also check English text
            ocr_results_en = ocr_service.detect_text(screenshot, "English")
            if ocr_results_en:
                self.logger.info("English text found:")
                for i, block in enumerate(ocr_results_en):
                    text = block.get('text', '').strip()
                    box = block.get('box', [])
                    if box and len(box) >= 4:
                        x1, y1 = box[0]
                        x2, y2 = box[2]
                        self.logger.info(f"  [{i+1}] '{text}' at ({int(x1)}, {int(y1)}) - ({int(x2)}, {int(y2)})")
                    else:
                        self.logger.info(f"  [{i+1}] '{text}' (no coordinates)")
            else:
                self.logger.info("No English text found")
            
            self.logger.info("=== END COLLECTION SEARCH DEBUG ===")
            
            # Try English "Collection" as fallback
            self.logger.info("Trying English 'Collection' as fallback...")
            coords = ocr_service.find_text_in_region(screenshot, "Collection", (0, 0, width, height), "English")
            if coords:
                center_x = coords[0] + coords[2] // 2
                center_y = coords[1] + coords[3] // 2
                self.logger.info(f"FOUND 'Collection' at coordinates: ({center_x}, {center_y})")
                return window_service.click_in_window(window, center_x, center_y)
            
            self.logger.warning("Neither '我的收藏' nor 'Collection' found")
            return False
            
        except Exception as e:
            self.logger.error(f"Error finding collection button: {e}")
            return False 