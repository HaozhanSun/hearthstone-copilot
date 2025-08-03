#!/usr/bin/env python3
"""
Hearthstone Bot - Automated Hearthstone Game Bot

This bot can:
1. Detect and focus the Hearthstone game window
2. Take screenshots and recognize cards using OCR
3. Analyze the current game state
4. Make strategic decisions about which cards to play
5. Automate mouse and keyboard actions to play the game

Usage:
    python main.py [--test] [--debug] [--auto-play]

Options:
    --test: Run in test mode (no actual gameplay)
    --debug: Enable debug logging
    --auto-play: Enable automatic gameplay
"""

import argparse
import logging
import time
import sys
import cv2
import numpy as np
from typing import Dict, Optional

# Import our modules
from automation.window_utils import focus_hearthstone_window, get_hearthstone_screenshot
from game_state.game_analyzer import GameAnalyzer
from decision_engine.ai_engine import AIEngine
from automation.input_controller import InputController


class HearthstoneBot:
    """Main bot class that coordinates all components"""
    
    def __init__(self, debug: bool = False, auto_play: bool = False):
        self.debug = debug
        self.auto_play = auto_play
        self.running = False
        
        # Setup logging
        self._setup_logging()
        
        # Initialize components
        self.game_analyzer = GameAnalyzer()
        self.ai_engine = AIEngine()
        self.input_controller = InputController()
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Hearthstone Bot initialized")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        level = logging.DEBUG if self.debug else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('hearthstone_bot.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def start(self):
        """Start the bot"""
        self.logger.info("Starting Hearthstone Bot...")
        
        # Check if Hearthstone is running
        if not focus_hearthstone_window():
            self.logger.error("Hearthstone window not found. Please start Hearthstone first.")
            return False
        
        self.logger.info("Hearthstone window found and focused")
        self.running = True
        
        if self.auto_play:
            self.run_auto_play()
        else:
            self.run_analysis_mode()
        
        return True
    
    def run_analysis_mode(self):
        """Run in analysis mode - just analyze game state without playing"""
        self.logger.info("Running in analysis mode")
        
        try:
            while self.running:
                # Take screenshot
                screenshot = get_hearthstone_screenshot()
                if screenshot is None:
                    self.logger.warning("Failed to capture screenshot")
                    time.sleep(1)
                    continue
                
                # Analyze game state
                game_state = self.game_analyzer.analyze_game_state(screenshot)
                
                # Display analysis
                self._display_analysis(game_state)
                
                # Wait before next analysis
                time.sleep(2)
                
        except KeyboardInterrupt:
            self.logger.info("Analysis mode stopped by user")
        except Exception as e:
            self.logger.error(f"Error in analysis mode: {e}")
    
    def run_auto_play(self):
        """Run in auto-play mode - analyze and make moves automatically"""
        self.logger.info("Running in auto-play mode")
        
        try:
            while self.running:
                # Take screenshot
                screenshot = get_hearthstone_screenshot()
                if screenshot is None:
                    self.logger.warning("Failed to capture screenshot")
                    time.sleep(1)
                    continue
                
                # Analyze game state
                game_state = self.game_analyzer.analyze_game_state(screenshot)
                
                # Display current state
                self._display_analysis(game_state)
                
                # Make decision
                decision = self.ai_engine.decide_next_move(game_state)
                
                # Execute decision
                self._execute_decision(decision, game_state)
                
                # Wait before next iteration
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Auto-play mode stopped by user")
        except Exception as e:
            self.logger.error(f"Error in auto-play mode: {e}")
    
    def _display_analysis(self, game_state: Dict):
        """Display the current game analysis"""
        print("\n" + "="*50)
        print("GAME STATE ANALYSIS")
        print("="*50)
        
        # Display hand cards
        hand_cards = game_state.get('hand_cards', [])
        print(f"Hand Cards ({len(hand_cards)}):")
        for i, card in enumerate(hand_cards):
            name = card.get('name', 'Unknown')
            cost = card.get('cost', '?')
            attack = card.get('attack', '')
            health = card.get('health', '')
            stats = f"({attack}/{health})" if attack and health else ""
            print(f"  {i+1}. {name} [{cost}] {stats}")
        
        # Display board state
        board_state = game_state.get('board_state', {})
        friendly_minions = board_state.get('friendly_minions', [])
        enemy_minions = board_state.get('enemy_minions', [])
        
        print(f"\nBoard State:")
        print(f"  Friendly Minions: {len(friendly_minions)}")
        print(f"  Enemy Minions: {len(enemy_minions)}")
        
        # Display mana
        mana_info = game_state.get('mana', {})
        current_mana = mana_info.get('current_mana', 0)
        print(f"\nMana: {current_mana}")
        
        # Display game phase
        game_phase = game_state.get('game_phase', 'unknown')
        print(f"Game Phase: {game_phase}")
        
        print("="*50)
    
    def _execute_decision(self, decision: Dict, game_state: Dict):
        """Execute the AI decision"""
        action = decision.get('action', 'wait')
        reason = decision.get('reason', 'No reason given')
        
        self.logger.info(f"Executing action: {action} - {reason}")
        
        if action == 'wait':
            self.logger.info("Waiting for turn...")
            time.sleep(2)
        
        elif action == 'end_turn':
            self.logger.info("Ending turn...")
            self.input_controller.click_end_turn()
            time.sleep(1)
        
        elif action == 'play_card':
            card = decision.get('card')
            target = decision.get('target', 'board')
            
            if card:
                self.logger.info(f"Playing card: {card.get('name', 'Unknown')} -> {target}")
                
                # Find card position in hand
                hand_cards = game_state.get('hand_cards', [])
                card_position = None
                for i, hand_card in enumerate(hand_cards):
                    if hand_card.get('name') == card.get('name'):
                        card_position = i
                        break
                
                if card_position is not None:
                    if target == 'board':
                        # Play minion on board
                        self.input_controller.click_card_in_hand(card_position, len(hand_cards))
                        time.sleep(0.5)
                        self.input_controller.click_on_board((0.5, 0.5))  # Center of board
                    
                    elif target == 'opponent_face':
                        # Play spell on opponent
                        self.input_controller.click_card_in_hand(card_position, len(hand_cards))
                        time.sleep(0.5)
                        self.input_controller.click_opponent_face()
                    
                    elif target == 'enemy_minion':
                        # Play spell on enemy minion
                        self.input_controller.click_card_in_hand(card_position, len(hand_cards))
                        time.sleep(0.5)
                        self.input_controller.click_on_board((0.5, 0.3))  # Enemy board area
                    
                    elif target == 'friendly_minion':
                        # Play buff on friendly minion
                        self.input_controller.click_card_in_hand(card_position, len(hand_cards))
                        time.sleep(0.5)
                        self.input_controller.click_on_board((0.5, 0.7))  # Friendly board area
                    
                    elif target == 'self':
                        # Play spell on self
                        self.input_controller.click_card_in_hand(card_position, len(hand_cards))
                        time.sleep(0.5)
                        self.input_controller.click_own_face()
                
                # Wait for animation
                self.input_controller.wait_for_animation()
        
        else:
            self.logger.warning(f"Unknown action: {action}")
    
    def stop(self):
        """Stop the bot"""
        self.logger.info("Stopping Hearthstone Bot...")
        self.running = False
    
    def test_components(self):
        """Test individual components"""
        self.logger.info("Testing bot components...")
        
        # Test window detection
        if focus_hearthstone_window():
            self.logger.info("✓ Window detection works")
        else:
            self.logger.error("✗ Window detection failed")
            return False
        
        # Test screenshot capture
        screenshot = get_hearthstone_screenshot()
        if screenshot is not None:
            self.logger.info(f"✓ Screenshot capture works (shape: {screenshot.shape})")
            
            # Save test screenshot
            cv2.imwrite("test_screenshot.png", cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR))
            self.logger.info("✓ Test screenshot saved as 'test_screenshot.png'")
        else:
            self.logger.error("✗ Screenshot capture failed")
            return False
        
        # Test game analysis
        try:
            game_state = self.game_analyzer.analyze_game_state(screenshot)
            self.logger.info("✓ Game analysis works")
            self.logger.info(f"  - Detected {len(game_state.get('hand_cards', []))} cards in hand")
            self.logger.info(f"  - Current mana: {game_state.get('mana', {}).get('current_mana', 0)}")
        except Exception as e:
            self.logger.error(f"✗ Game analysis failed: {e}")
            return False
        
        # Test AI decision making
        try:
            decision = self.ai_engine.decide_next_move(game_state)
            self.logger.info("✓ AI decision making works")
            self.logger.info(f"  - Decision: {decision.get('action', 'unknown')}")
        except Exception as e:
            self.logger.error(f"✗ AI decision making failed: {e}")
            return False
        
        self.logger.info("All component tests passed!")
        return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Hearthstone Bot")
    parser.add_argument("--test", action="store_true", help="Run component tests")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--auto-play", action="store_true", help="Enable automatic gameplay")
    
    args = parser.parse_args()
    
    # Create bot instance
    bot = HearthstoneBot(debug=args.debug, auto_play=args.auto_play)
    
    if args.test:
        # Run tests
        success = bot.test_components()
        if success:
            print("\n🎉 All tests passed! The bot is ready to use.")
        else:
            print("\n❌ Some tests failed. Please check the logs.")
        return
    
    # Start the bot
    try:
        bot.start()
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main() 