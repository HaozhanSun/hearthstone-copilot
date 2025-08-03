import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
from card_recognition import CardDetector, OCRReader, CardDatabase


class GameAnalyzer:
    """Analyzes the current state of a Hearthstone game"""
    
    def __init__(self):
        self.card_detector = CardDetector()
        self.ocr_reader = OCRReader()
        self.card_database = CardDatabase()
    
    def analyze_game_state(self, screenshot: np.ndarray) -> Dict:
        """Analyze the complete game state from a screenshot"""
        # Focus the game window first
        from automation.window_utils import focus_hearthstone_window
        focus_hearthstone_window()
        
        # Extract different regions
        hand_region = self._get_hand_region(screenshot)
        board_region = self._get_board_region(screenshot)
        mana_region = self._get_mana_region(screenshot)
        
        # Analyze each component
        hand_cards = self.analyze_hand(hand_region)
        board_state = self.analyze_board(board_region)
        mana_info = self.analyze_mana(mana_region)
        game_phase = self.detect_game_phase(screenshot)
        
        return {
            'hand_cards': hand_cards,
            'board_state': board_state,
            'mana': mana_info,
            'game_phase': game_phase,
            'turn_number': self._estimate_turn_number(mana_info['current_mana']),
            'timestamp': self._get_timestamp()
        }
    
    def analyze_hand(self, hand_region: np.ndarray) -> List[Dict]:
        """Analyze cards in hand"""
        if hand_region is None:
            return []
        
        # Detect card boundaries
        card_rectangles = self.card_detector.detect_cards_in_hand(hand_region)
        
        hand_cards = []
        for i, rect in enumerate(card_rectangles):
            # Extract individual card image
            card_image = self.card_detector.extract_card_image(hand_region, rect)
            
            # Extract card information using OCR
            card_info = self.ocr_reader.extract_all_card_info(card_image)
            
            # Try to match with database
            if card_info['name']:
                matched_name = self.card_database.fuzzy_match_card(card_info['name'])
                if matched_name:
                    card_info['name'] = matched_name
                    # Get additional info from database
                    db_card = self.card_database.get_card(matched_name)
                    if db_card:
                        card_info.update(db_card)
            
            # Add position information
            card_info['position'] = i
            card_info['rectangle'] = rect
            
            hand_cards.append(card_info)
        
        return hand_cards
    
    def analyze_board(self, board_region: np.ndarray) -> Dict:
        """Analyze the game board state"""
        if board_region is None:
            return {'friendly_minions': [], 'enemy_minions': []}
        
        # Detect cards on board
        card_rectangles = self.card_detector.detect_cards_on_board(board_region)
        
        friendly_minions = []
        enemy_minions = []
        
        # This is a simplified approach - would need more sophisticated detection
        # to distinguish between friendly and enemy minions
        for rect in card_rectangles:
            card_image = self.card_detector.extract_card_image(board_region, rect)
            card_info = self.ocr_reader.extract_all_card_info(card_image)
            
            # For now, assume all detected cards are friendly
            # In a real implementation, you'd need to detect ownership
            friendly_minions.append(card_info)
        
        return {
            'friendly_minions': friendly_minions,
            'enemy_minions': enemy_minions,
            'total_minions': len(friendly_minions) + len(enemy_minions)
        }
    
    def analyze_mana(self, mana_region: np.ndarray) -> Dict:
        """Analyze mana information"""
        if mana_region is None:
            return {'current_mana': 0, 'max_mana': 10}
        
        # Use both computer vision and OCR for mana detection
        cv_mana = self.card_detector.detect_mana_crystals(mana_region)
        ocr_mana = self.ocr_reader.extract_mana_crystals(mana_region)
        
        # Use the more reliable method
        current_mana = cv_mana if cv_mana > 0 else ocr_mana
        
        return {
            'current_mana': current_mana,
            'max_mana': min(10, current_mana + 1),  # Estimate max mana
            'mana_spent': 0  # Would need to track over time
        }
    
    def detect_game_phase(self, screenshot: np.ndarray) -> str:
        """Detect the current game phase"""
        # Look for specific UI elements that indicate game phase
        
        # Convert to HSV for color detection
        hsv = cv2.cvtColor(screenshot, cv2.COLOR_RGB2HSV)
        
        # Check for mulligan screen (usually has specific colors)
        # This is a simplified detection - would need more sophisticated analysis
        
        # Check for end turn button (usually green)
        green_lower = np.array([40, 50, 50])
        green_upper = np.array([80, 255, 255])
        green_mask = cv2.inRange(hsv, green_lower, green_upper)
        
        if np.sum(green_mask) > 1000:  # Threshold for green detection
            return "my_turn"
        
        # Check for opponent turn indicators
        # This would need more specific detection logic
        
        return "unknown"
    
    def get_playable_cards(self, hand_cards: List[Dict], current_mana: int) -> List[Dict]:
        """Get cards that can be played with current mana"""
        playable = []
        
        for card in hand_cards:
            card_cost = card.get('cost', 0)
            if card_cost <= current_mana:
                playable.append(card)
        
        return playable
    
    def calculate_board_value(self, minions: List[Dict]) -> Dict:
        """Calculate the total value of minions on board"""
        total_attack = sum(minion.get('attack', 0) for minion in minions)
        total_health = sum(minion.get('health', 0) for minion in minions)
        
        return {
            'total_attack': total_attack,
            'total_health': total_health,
            'minion_count': len(minions),
            'average_attack': total_attack / len(minions) if minions else 0,
            'average_health': total_health / len(minions) if minions else 0
        }
    
    def _get_hand_region(self, screenshot: np.ndarray) -> Optional[np.ndarray]:
        """Extract hand region from screenshot"""
        from ..automation.window_utils import get_game_region_screenshot
        return get_game_region_screenshot('hand')
    
    def _get_board_region(self, screenshot: np.ndarray) -> Optional[np.ndarray]:
        """Extract board region from screenshot"""
        from ..automation.window_utils import get_game_region_screenshot
        return get_game_region_screenshot('board')
    
    def _get_mana_region(self, screenshot: np.ndarray) -> Optional[np.ndarray]:
        """Extract mana region from screenshot"""
        from ..automation.window_utils import get_game_region_screenshot
        return get_game_region_screenshot('mana')
    
    def _estimate_turn_number(self, current_mana: int) -> int:
        """Estimate current turn number based on mana"""
        # Early game: turns 1-4
        if current_mana <= 4:
            return current_mana
        # Mid game: turns 5-7
        elif current_mana <= 7:
            return current_mana
        # Late game: turns 8+
        else:
            return current_mana
    
    def _get_timestamp(self) -> float:
        """Get current timestamp"""
        import time
        return time.time() 