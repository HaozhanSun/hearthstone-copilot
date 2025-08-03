"""
OCR service for the Hearthstone Bot
"""

import cv2
import numpy as np
import base64
import requests
import re
from typing import List, Dict, Optional, Tuple, Set
from core.exceptions import OCRException


class OCRService:
    """Service for OCR operations using Umi-OCR"""
    
    def __init__(self, logger, base_url: str = "http://127.0.0.1:1224"):
        self.logger = logger
        self.base_url = base_url
    
    def detect_text(self, image: np.ndarray, language: str = "English") -> List[Dict]:
        """Detect text in image using Umi-OCR"""
        try:
            # Convert image to base64
            _, buffer = cv2.imencode('.png', image)
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Prepare OCR request
            ocr_data = {
                "base64": image_base64,
                "options": {
                    "ocr.language": language,
                    "ocr.maxSideLen": 1024,
                    "tbpu.parser": "multi_para",
                    "data.format": "dict"
                }
            }
            
            # Send request to Umi-OCR service
            response = requests.post(
                f"{self.base_url}/api/ocr",
                json=ocr_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code != 200:
                raise OCRException(f"OCR service returned status {response.status_code}")
            
            result = response.json()
            if result.get('code') != 100:
                raise OCRException(f"OCR service error: {result.get('message', 'Unknown error')}")
            
            return result.get('data', [])
            
        except Exception as e:
            import traceback
            stack_trace = traceback.format_exc()
            self.logger.error(f"Error in OCR detection: {e}")
            self.logger.error(f"Stack trace:\n{stack_trace}")
            raise OCRException(f"OCR detection failed: {e}\nStack trace:\n{stack_trace}")
    
    def find_text_in_region(self, image: np.ndarray, target_text: str, 
                           region: Tuple[int, int, int, int], 
                           language: str = "English") -> Optional[Tuple[int, int, int, int]]:
        """Find specific text in a region and return coordinates"""
        try:
            # Crop image to region
            x1, y1, x2, y2 = region
            cropped_image = image[y1:y2, x1:x2]
            
            # Detect text in cropped region
            ocr_results = self.detect_text(cropped_image, language)
            
            # Look for target text
            for block in ocr_results:
                text = block.get('text', '').strip()
                if self._text_matches(text, target_text):
                    box = block.get('box', [])
                    if len(box) >= 4:
                        # Convert relative coordinates back to absolute
                        rel_x1, rel_y1 = box[0]
                        rel_x2, rel_y2 = box[2]
                        # Ensure we're working with scalar values, not numpy arrays
                        abs_x1 = x1 + int(float(rel_x1))
                        abs_y1 = y1 + int(float(rel_y1))
                        abs_x2 = x1 + int(float(rel_x2))
                        abs_y2 = y1 + int(float(rel_y2))
                        
                        return (abs_x1, abs_y1, abs_x2 - abs_x1, abs_y2 - abs_y1)
            
            return None
            
        except Exception as e:
            import traceback
            stack_trace = traceback.format_exc()
            self.logger.error(f"Error finding text in region: {e}")
            self.logger.error(f"Stack trace:\n{stack_trace}")
            return None
    
    def find_chinese_characters(self, image: np.ndarray, target_chars: Set[str], 
                               region: Tuple[int, int, int, int] = None) -> Dict[str, Tuple[int, int, int, int]]:
        """Find specific Chinese characters in image and return their positions"""
        try:
            # Use Chinese OCR
            if region:
                x1, y1, x2, y2 = region
                cropped_image = image[y1:y2, x1:x2]
                ocr_results = self.detect_text(cropped_image, "简体中文")
            else:
                ocr_results = self.detect_text(image, "简体中文")
            
            char_positions = {}
            all_chinese_chars = set()
            
            for block in ocr_results:
                text = block.get('text', '').strip()
                box = block.get('box', [])
                
                if box and len(box) >= 4:
                    x1, y1 = box[0]
                    x2, y2 = box[2]
                    # Ensure we're working with scalar values, not numpy arrays
                    text_x = int(float(x1))
                    text_y = int(float(y1))
                    text_w = int(float(x2) - float(x1))
                    text_h = int(float(y2) - float(y1))
                    
                    # Extract Chinese characters from this text block
                    chinese_chars = self._extract_chinese_characters(text)
                    
                    # Calculate individual character positions
                    if chinese_chars:
                        chinese_char_count = len(chinese_chars)
                        if chinese_char_count > 0:
                            char_width = text_w // chinese_char_count
                            for i, char in enumerate(chinese_chars):
                                all_chinese_chars.add(char)
                                # Calculate position of this character within the text block
                                char_x = text_x + (i * char_width)
                                char_w = char_width
                                char_y = text_y
                                char_h = text_h
                                
                                # Convert to absolute coordinates if region was specified
                                if region:
                                    char_x += region[0]
                                    char_y += region[1]
                                
                                char_positions[char] = (char_x, char_y, char_w, char_h)
            
            # Return only positions for target characters
            return {char: pos for char, pos in char_positions.items() if char in target_chars}
            
        except Exception as e:
            import traceback
            stack_trace = traceback.format_exc()
            self.logger.error(f"Error finding Chinese characters: {e}")
            self.logger.error(f"Stack trace:\n{stack_trace}")
            return {}
    
    def _text_matches(self, detected_text: str, target_text: str) -> bool:
        """Check if detected text matches target text"""
        # Direct match
        if target_text in detected_text or detected_text in target_text:
            return True
        
        # Case-insensitive match
        if detected_text.lower() == target_text.lower():
            return True
        
        # Additional patterns for "我的收藏"
        if "我的收藏" in target_text:
            patterns = [
                "我的收藏", "我的", "收藏", 
                "My Collection", "Collection", "My collection",
                "MY COLLECTION", "COLLECTION",
                "my collection", "collection",
                "收藏夹", "我的收藏夹", "卡牌收藏", "卡牌",
                "Collection Tab", "Cards", "My Cards", "Card Collection",
                "COLLECTION TAB", "CARDS", "MY CARDS", "CARD COLLECTION"
            ]
            for pattern in patterns:
                if pattern in detected_text:
                    return True
        
        return False
    
    def _extract_chinese_characters(self, text: str) -> List[str]:
        """Extract all Chinese characters from text"""
        # Unicode range for Chinese characters
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
        return chinese_pattern.findall(text)
    
    def check_service_status(self) -> bool:
        """Check if Umi-OCR service is running"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=3)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False 