import pyautogui
import time
import win32gui
import win32con
from typing import Tuple, Optional
import logging


class InputController:
    """Handles mouse and keyboard input for Hearthstone automation"""
    
    def __init__(self, safety_delay: float = 0.1):
        self.safety_delay = safety_delay
        self.logger = logging.getLogger(__name__)
        
        # Configure pyautogui for safety
        pyautogui.FAILSAFE = True  # Move mouse to corner to stop
        pyautogui.PAUSE = safety_delay
        
        # Get screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
    
    def click_card_in_hand(self, card_position: int, total_cards: int) -> bool:
        """Click on a specific card in hand"""
        try:
            # Calculate card position based on hand layout
            # Cards are typically arranged horizontally in the bottom area
            window = self._get_hearthstone_window()
            if not window:
                return False
            
            # Calculate card positions (simplified)
            card_width = window.width // total_cards
            card_x = window.left + (card_position * card_width) + (card_width // 2)
            card_y = window.top + window.height - 100  # Approximate hand position
            
            # Click on the card
            pyautogui.click(card_x, card_y)
            time.sleep(self.safety_delay)
            
            self.logger.info(f"Clicked card at position {card_position}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error clicking card: {e}")
            return False
    
    def click_on_board(self, board_position: Tuple[int, int]) -> bool:
        """Click on a specific position on the game board"""
        try:
            window = self._get_hearthstone_window()
            if not window:
                return False
            
            # Convert relative board position to screen coordinates
            board_x = window.left + int(window.width * board_position[0])
            board_y = window.top + int(window.height * board_position[1])
            
            pyautogui.click(board_x, board_y)
            time.sleep(self.safety_delay)
            
            self.logger.info(f"Clicked board at position {board_position}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error clicking board: {e}")
            return False
    
    def click_hero_power(self) -> bool:
        """Click the hero power button"""
        try:
            window = self._get_hearthstone_window()
            if not window:
                return False
            
            # Hero power is typically in the bottom-right area
            hero_x = window.left + window.width - 100
            hero_y = window.top + window.height - 150
            
            pyautogui.click(hero_x, hero_y)
            time.sleep(self.safety_delay)
            
            self.logger.info("Clicked hero power")
            return True
            
        except Exception as e:
            self.logger.error(f"Error clicking hero power: {e}")
            return False
    
    def click_end_turn(self) -> bool:
        """Click the end turn button"""
        try:
            window = self._get_hearthstone_window()
            if not window:
                return False
            
            # End turn button is typically in the bottom-right
            end_turn_x = window.left + window.width - 80
            end_turn_y = window.top + window.height - 50
            
            pyautogui.click(end_turn_x, end_turn_y)
            time.sleep(self.safety_delay)
            
            self.logger.info("Clicked end turn")
            return True
            
        except Exception as e:
            self.logger.error(f"Error clicking end turn: {e}")
            return False
    
    def drag_card_to_target(self, card_position: int, target_position: Tuple[int, int]) -> bool:
        """Drag a card from hand to a target position"""
        try:
            window = self._get_hearthstone_window()
            if not window:
                return False
            
            # Calculate source position (card in hand)
            card_x = window.left + (card_position * 80) + 40  # Approximate card width
            card_y = window.top + window.height - 80
            
            # Calculate target position
            target_x = window.left + int(window.width * target_position[0])
            target_y = window.top + int(window.height * target_position[1])
            
            # Perform drag operation
            pyautogui.moveTo(card_x, card_y)
            time.sleep(0.1)
            pyautogui.dragTo(target_x, target_y, duration=0.5)
            time.sleep(self.safety_delay)
            
            self.logger.info(f"Dragged card from position {card_position} to {target_position}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error dragging card: {e}")
            return False
    
    def click_opponent_face(self) -> bool:
        """Click on the opponent's hero face"""
        try:
            window = self._get_hearthstone_window()
            if not window:
                return False
            
            # Opponent face is typically in the top area
            face_x = window.left + (window.width // 2)
            face_y = window.top + 100
            
            pyautogui.click(face_x, face_y)
            time.sleep(self.safety_delay)
            
            self.logger.info("Clicked opponent face")
            return True
            
        except Exception as e:
            self.logger.error(f"Error clicking opponent face: {e}")
            return False
    
    def click_own_face(self) -> bool:
        """Click on own hero face"""
        try:
            window = self._get_hearthstone_window()
            if not window:
                return False
            
            # Own face is typically in the bottom area
            face_x = window.left + (window.width // 2)
            face_y = window.top + window.height - 200
            
            pyautogui.click(face_x, face_y)
            time.sleep(self.safety_delay)
            
            self.logger.info("Clicked own face")
            return True
            
        except Exception as e:
            self.logger.error(f"Error clicking own face: {e}")
            return False
    
    def press_key(self, key: str) -> bool:
        """Press a specific key"""
        try:
            pyautogui.press(key)
            time.sleep(self.safety_delay)
            
            self.logger.info(f"Pressed key: {key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error pressing key {key}: {e}")
            return False
    
    def type_text(self, text: str) -> bool:
        """Type text (for chat or search)"""
        try:
            pyautogui.typewrite(text)
            time.sleep(self.safety_delay)
            
            self.logger.info(f"Typed text: {text}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error typing text: {e}")
            return False
    
    def wait_for_animation(self, duration: float = 2.0):
        """Wait for game animations to complete"""
        time.sleep(duration)
        self.logger.info(f"Waited {duration} seconds for animation")
    
    def _get_hearthstone_window(self) -> Optional[object]:
        """Get the Hearthstone window object"""
        from .window_utils import find_hearthstone_window
        return find_hearthstone_window()
    
    def emergency_stop(self):
        """Emergency stop function - move mouse to corner"""
        try:
            pyautogui.moveTo(0, 0)
            self.logger.warning("Emergency stop activated")
        except Exception as e:
            self.logger.error(f"Error in emergency stop: {e}")
    
    def is_safe_to_click(self, x: int, y: int) -> bool:
        """Check if a position is safe to click (within screen bounds)"""
        return 0 <= x <= self.screen_width and 0 <= y <= self.screen_height 