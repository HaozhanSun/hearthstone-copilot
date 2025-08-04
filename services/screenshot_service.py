"""
Screenshot service for the Hearthstone Bot
"""

import cv2
import numpy as np
import pyautogui
from typing import Optional, Tuple
from core.exceptions import ScreenshotException


class ScreenshotService:
    """Service for capturing and processing screenshots"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[np.ndarray]:
        """Capture full screen screenshot or region"""
        try:
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()
            screenshot_np = np.array(screenshot)
            screenshot_rgb = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            return screenshot_rgb
        except Exception as e:
            self.logger.error(f"Error capturing screen: {e}")
            return None
    
    def capture_window(self, x: int, y: int, width: int, height: int) -> Optional[np.ndarray]:
        """Capture screenshot of specific window region"""
        try:
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            screenshot_np = np.array(screenshot)
            screenshot_rgb = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            return screenshot_rgb
        except Exception as e:
            self.logger.error(f"Error capturing window region: {e}")
            return None
    
    def capture_window_object(self, window) -> Optional[np.ndarray]:
        """Capture screenshot of a window object"""
        try:
            x, y, width, height = window.left, window.top, window.width, window.height
            return self.capture_window(x, y, width, height)
        except Exception as e:
            self.logger.error(f"Error capturing window object: {e}")
            return None
    
    def preprocess_for_ocr(self, image: np.ndarray, language: str = "English") -> np.ndarray:
        """Preprocess image for better OCR results"""
        try:
            if "点击" in language or "我的" in language or language == "简体中文":
                # For Chinese text, use original image to avoid preprocessing interference
                return image
            else:
                # Apply preprocessing for English text
                # Convert to grayscale for better text detection
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                
                # Apply slight blur to reduce noise
                blurred = cv2.GaussianBlur(gray, (1, 1), 0)
                
                # Apply adaptive thresholding to improve text contrast
                thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
                
                # Convert back to BGR for consistency
                return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
                
        except Exception as e:
            self.logger.error(f"Error preprocessing image: {e}")
            return image
    
    def create_debug_image(self, image: np.ndarray) -> np.ndarray:
        """Create a copy of image for debug annotations"""
        return image.copy()
    
    def draw_search_region(self, image: np.ndarray, region: Tuple[int, int, int, int], 
                          label: str = "SEARCH AREA") -> np.ndarray:
        """Draw search region rectangle on image"""
        try:
            x1, y1, x2, y2 = region
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green rectangle
            cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            return image
        except Exception as e:
            self.logger.error(f"Error drawing search region: {e}")
            return image
    
    def draw_text_region(self, image: np.ndarray, x: int, y: int, width: int, height: int, 
                        label: str, color: Tuple[int, int, int] = (0, 255, 255)) -> np.ndarray:
        """Draw text region rectangle on image"""
        try:
            cv2.rectangle(image, (x, y), (x + width, y + height), color, 2)
            cv2.putText(image, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            return image
        except Exception as e:
            self.logger.error(f"Error drawing text region: {e}")
            return image
    
    def get_image_size(self, image: np.ndarray) -> Tuple[int, int]:
        """Get image dimensions"""
        height, width = image.shape[:2]
        return width, height
    
    def save_screenshot(self, image: np.ndarray, filepath: str) -> bool:
        """Save screenshot to file"""
        try:
            cv2.imwrite(filepath, image)
            return True
        except Exception as e:
            self.logger.error(f"Error saving screenshot to {filepath}: {e}")
            return False 