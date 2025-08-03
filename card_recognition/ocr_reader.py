import cv2
import numpy as np
import pytesseract
from typing import Optional, List
import re


class OCRReader:
    """OCR reader for extracting text from Hearthstone screenshots"""
    
    def __init__(self):
        # Configure tesseract for better text recognition
        self.config = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz '
    
    def preprocess_image_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image to improve OCR accuracy"""
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Apply threshold to get binary image
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Apply morphological operations to clean up text
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    def extract_card_name(self, card_image: np.ndarray) -> Optional[str]:
        """Extract card name from card image"""
        # Focus on the top portion where card name is typically located
        height, width = card_image.shape[:2]
        name_region = card_image[int(height*0.1):int(height*0.3), int(width*0.1):int(width*0.9)]
        
        # Preprocess for OCR
        processed = self.preprocess_image_for_ocr(name_region)
        
        # Extract text
        text = pytesseract.image_to_string(processed, config=self.config)
        
        # Clean up text
        cleaned_text = self.clean_ocr_text(text)
        
        return cleaned_text if cleaned_text else None
    
    def extract_card_cost(self, card_image: np.ndarray) -> Optional[int]:
        """Extract mana cost from card image"""
        # Focus on top-left corner where mana cost is located
        height, width = card_image.shape[:2]
        cost_region = card_image[int(height*0.05):int(height*0.25), int(width*0.05):int(width*0.25)]
        
        # Preprocess for OCR
        processed = self.preprocess_image_for_ocr(cost_region)
        
        # Extract text
        text = pytesseract.image_to_string(processed, config='--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789')
        
        # Try to extract number
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        
        return None
    
    def extract_card_stats(self, card_image: np.ndarray) -> tuple[Optional[int], Optional[int]]:
        """Extract attack and health from card image"""
        # Focus on bottom-right corner where stats are located
        height, width = card_image.shape[:2]
        stats_region = card_image[int(height*0.7):int(height*0.9), int(width*0.7):int(width*0.9)]
        
        # Preprocess for OCR
        processed = self.preprocess_image_for_ocr(stats_region)
        
        # Extract text
        text = pytesseract.image_to_string(processed, config='--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789/')
        
        # Try to extract attack/health format (e.g., "3/4")
        stats_match = re.search(r'(\d+)/(\d+)', text)
        if stats_match:
            attack = int(stats_match.group(1))
            health = int(stats_match.group(2))
            return attack, health
        
        # Try to extract individual numbers
        numbers = re.findall(r'\d+', text)
        if len(numbers) >= 2:
            return int(numbers[0]), int(numbers[1])
        
        return None, None
    
    def extract_mana_crystals(self, mana_region: np.ndarray) -> int:
        """Extract current mana from mana crystal region"""
        processed = self.preprocess_image_for_ocr(mana_region)
        text = pytesseract.image_to_string(processed, config='--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789')
        
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        
        return 0
    
    def extract_health(self, health_region: np.ndarray) -> int:
        """Extract health value from health region"""
        processed = self.preprocess_image_for_ocr(health_region)
        text = pytesseract.image_to_string(processed, config='--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789')
        
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        
        return 30  # Default health
    
    def extract_game_phase(self, screenshot: np.ndarray) -> str:
        """Extract current game phase from screenshot"""
        # Look for specific UI elements that indicate game phase
        # This is a simplified version - would need more sophisticated detection
        
        # Convert to HSV for color detection
        hsv = cv2.cvtColor(screenshot, cv2.COLOR_RGB2HSV)
        
        # Look for mulligan screen (usually has specific colors)
        # This is a placeholder - would need actual color analysis
        return "playing"  # Default to playing phase
    
    def clean_ocr_text(self, text: str) -> str:
        """Clean up OCR text output"""
        # Remove extra whitespace and newlines
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters that aren't part of card names
        cleaned = re.sub(r'[^\w\s]', '', cleaned)
        
        return cleaned
    
    def extract_all_card_info(self, card_image: np.ndarray) -> dict:
        """Extract all available information from a card image"""
        return {
            'name': self.extract_card_name(card_image),
            'cost': self.extract_card_cost(card_image),
            'attack': self.extract_card_stats(card_image)[0],
            'health': self.extract_card_stats(card_image)[1]
        } 