import cv2
import numpy as np
from typing import List, Tuple, Optional
import os


class CardDetector:
    """Detects cards in Hearthstone screenshots"""
    
    def __init__(self):
        self.card_templates = {}
        self.load_card_templates()
    
    def load_card_templates(self):
        """Load card template images for matching"""
        # This would load from a templates directory
        # For now, we'll use basic contour detection
        pass
    
    def detect_cards_in_hand(self, screenshot: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect card boundaries in hand region"""
        # Convert to grayscale
        gray = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Use Canny edge detection
        edges = cv2.Canny(blurred, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        card_rectangles = []
        
        for contour in contours:
            # Approximate the contour to a polygon
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(approx)
            
            # Filter by size (cards should be roughly rectangular)
            aspect_ratio = w / h if h > 0 else 0
            area = w * h
            
            # Typical card aspect ratio is around 0.7-0.8
            if 0.6 < aspect_ratio < 0.9 and area > 1000:
                card_rectangles.append((x, y, w, h))
        
        # Sort by x position (left to right)
        card_rectangles.sort(key=lambda rect: rect[0])
        
        return card_rectangles
    
    def detect_cards_on_board(self, screenshot: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect cards on the game board"""
        # Similar to hand detection but with different size constraints
        gray = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        card_rectangles = []
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h if h > 0 else 0
            area = w * h
            
            # Board cards might be slightly different size
            if 0.5 < aspect_ratio < 1.0 and area > 500:
                card_rectangles.append((x, y, w, h))
        
        return card_rectangles
    
    def extract_card_image(self, screenshot: np.ndarray, card_rect: Tuple[int, int, int, int]) -> np.ndarray:
        """Extract individual card image from screenshot"""
        x, y, w, h = card_rect
        return screenshot[y:y+h, x:x+w]
    
    def match_card_template(self, card_image: np.ndarray) -> Optional[str]:
        """Match card image against known templates"""
        # This would implement template matching
        # For now, return None (will be handled by OCR)
        return None
    
    def detect_mana_crystals(self, screenshot: np.ndarray) -> int:
        """Detect current mana crystals"""
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(screenshot, cv2.COLOR_RGB2HSV)
        
        # Define blue color range for mana crystals
        lower_blue = np.array([100, 50, 50])
        upper_blue = np.array([130, 255, 255])
        
        # Create mask for blue regions
        blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
        
        # Find contours of blue regions
        contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Count circular regions (mana crystals)
        crystal_count = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if 50 < area < 500:  # Reasonable size for mana crystals
                crystal_count += 1
        
        return min(crystal_count, 10)  # Cap at 10 mana
    
    def detect_health(self, screenshot: np.ndarray) -> int:
        """Detect hero health from screenshot"""
        # This would use OCR to read health numbers
        # For now, return placeholder
        return 30
    
    def detect_opponent_health(self, screenshot: np.ndarray) -> int:
        """Detect opponent health from screenshot"""
        # Similar to detect_health but for opponent
        return 30 