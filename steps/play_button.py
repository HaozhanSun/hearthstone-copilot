"""
Play Button Step for the Hearthstone Bot
"""

import time
from typing import Dict, Any, Optional, Tuple
from core.bot_state import BotState, BotContext
from core.exceptions import StepException
from .base_step import BaseStep


class PlayButtonStep(BaseStep):
    """Step to find and click the PLAY button in Battle.net"""
    
    def get_step_name(self) -> str:
        return "Play Button Detection"
    
    def can_skip(self, context: BotContext) -> bool:
        # Can skip if we already have a Battle.net window and it shows "playing now"
        window_service = self.services.get('window')
        if not window_service:
            return False
        
        battlenet_window = context.step_data.get('battlenet_window')
        if not battlenet_window:
            return False
        
        # Check if already playing
        return self._check_playing_status(battlenet_window)
    
    def execute(self, context: BotContext) -> BotContext:
        """Find and click the PLAY button"""
        try:
            window_service = self.services.get('window')
            screenshot_service = self.services.get('screenshot')
            ocr_service = self.services.get('ocr')
            
            if not all([window_service, screenshot_service, ocr_service]):
                raise StepException(self.get_step_name(), "Required services not available")
            
            # Get Battle.net window
            battlenet_window = context.step_data.get('battlenet_window')
            if not battlenet_window:
                battlenet_window = window_service.find_battlenet_window()
                if not battlenet_window:
                    raise StepException(self.get_step_name(), "Battle.net window not found")
                context.step_data['battlenet_window'] = battlenet_window
            
            # Focus the window
            if not window_service.focus_window(battlenet_window):
                # Try to refresh the window handle
                self.logger.warning("Failed to focus window, trying to refresh window handle...")
                battlenet_window = window_service.find_battlenet_window()
                if not battlenet_window:
                    raise StepException(self.get_step_name(), "Battle.net window not found after refresh")
                context.step_data['battlenet_window'] = battlenet_window
                
                if not window_service.focus_window(battlenet_window):
                    raise StepException(self.get_step_name(), "Failed to focus Battle.net window after refresh")
            
            # Get window region
            x, y, width, height = window_service.get_window_region(battlenet_window)
            
            # Try to find and click PLAY button
            max_attempts = 10
            for attempt in range(max_attempts):
                # Check if bot should stop
                if not self._check_bot_running(context):
                    return context
                
                # Take screenshot
                screenshot = screenshot_service.capture_window(x, y, width, height)
                if screenshot is None:
                    time.sleep(3)
                    continue
                
                # Save debug screenshot
                logger = self.services.get('logger')
                if logger:
                    logger.save_debug_screenshot(
                        screenshot, "battlenet_window", False, 
                        f"Window size: {width}x{height}", "play_button"
                    )
                
                # Check if already playing
                if self._check_playing_status_from_screenshot(screenshot, ocr_service):
                    self.logger.info("Hearthstone is already playing")
                    context.update_state(BotState.WAITING_FOR_HEARTHSTONE)
                    return context
                
                # Look for PLAY button
                play_coords = self._find_play_button(screenshot, ocr_service, width, height)
                if play_coords:
                    # Click PLAY button
                    if window_service.click_in_window(battlenet_window, play_coords[0], play_coords[1]):
                        self.logger.info(f"Clicked PLAY button at ({play_coords[0]}, {play_coords[1]})")
                        
                        # Wait and verify
                        time.sleep(1)
                        if self._verify_play_click(battlenet_window, window_service, screenshot_service, ocr_service):
                            context.update_state(BotState.WAITING_FOR_HEARTHSTONE)
                            return context
                        else:
                            self.logger.warning("PLAY button click verification failed, retrying")
                            continue
                    else:
                        self.logger.error("Failed to click PLAY button")
                        continue
                
                # Wait before retry
                time.sleep(3)
            
            raise StepException(self.get_step_name(), "Failed to find or click PLAY button after maximum attempts")
            
        except Exception as e:
            if isinstance(e, StepException):
                raise e
            raise StepException(self.get_step_name(), str(e))
    
    def _check_playing_status(self, window) -> bool:
        """Check if Hearthstone is already playing"""
        screenshot_service = self.services.get('screenshot')
        ocr_service = self.services.get('ocr')
        
        if not all([screenshot_service, ocr_service]):
            return False
        
        screenshot = screenshot_service.capture_window_object(window)
        if screenshot is None:
            return False
        
        return self._check_playing_status_from_screenshot(screenshot, ocr_service)
    
    def _check_playing_status_from_screenshot(self, screenshot, ocr_service) -> bool:
        """Check playing status from screenshot"""
        try:
            ocr_results = ocr_service.detect_text(screenshot, "English")
            for block in ocr_results:
                text = block.get('text', '').strip().upper()
                if "PLAYING NOW" in text or "PLAYING" in text:
                    return True
            return False
        except Exception:
            return False
    
    def _find_play_button(self, screenshot, ocr_service, window_width: int, window_height: int) -> Optional[Tuple[int, int]]:
        """Find PLAY button coordinates"""
        try:
            ocr_results = ocr_service.detect_text(screenshot, "English")
            
            # Define search region (bottom-left area)
            search_region_x1 = 0
            search_region_y1 = int(window_height * 0.7)
            search_region_x2 = int(window_width * 0.4)
            search_region_y2 = window_height
            
            # Look for "PLAY" text in the search region
            for block in ocr_results:
                text = block.get('text', '').strip()
                if text.upper() == "PLAY":
                    box = block.get('box', [])
                    if len(box) >= 4:
                        x1, y1 = box[0]
                        x2, y2 = box[2]
                        # Ensure we're working with scalar values, not numpy arrays
                        text_x = int(float(x1))
                        text_y = int(float(y1))
                        text_w = int(float(x2) - float(x1))
                        text_h = int(float(y2) - float(y1))
                        
                        # Check if text is in the search region
                        in_search_region = (text_x >= search_region_x1 and 
                                          text_x + text_w <= search_region_x2 and
                                          text_y >= search_region_y1 and 
                                          text_y + text_h <= search_region_y2)
                        
                        if in_search_region:
                            # Return center coordinates
                            center_x = text_x + text_w // 2
                            center_y = text_y + text_h // 2
                            return (center_x, center_y)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding PLAY button: {e}")
            return None
    
    def _verify_play_click(self, window, window_service, screenshot_service, ocr_service) -> bool:
        """Verify that PLAY button click was successful"""
        try:
            screenshot = screenshot_service.capture_window_object(window)
            if screenshot is None:
                return False
            
            ocr_results = ocr_service.detect_text(screenshot, "English")
            for block in ocr_results:
                text = block.get('text', '').strip().upper()
                if "LAUNCHING" in text or "PLAYING NOW" in text or "PLAYING" in text:
                    return True
            return False
            
        except Exception:
            return False
    
    def _check_bot_running(self, context: BotContext) -> bool:
        """Check if bot should continue running"""
        # This would be implemented based on the bot's running state
        # For now, return True
        return True 