from typing import Dict, List, Optional, Tuple
import random
import logging


class AIEngine:
    """AI engine for making strategic decisions in Hearthstone"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.difficulty = "medium"  # easy, medium, hard
    
    def decide_next_move(self, game_state: Dict) -> Dict:
        """Decide the next move based on current game state"""
        try:
            # Extract key information
            hand_cards = game_state.get('hand_cards', [])
            board_state = game_state.get('board_state', {})
            mana_info = game_state.get('mana', {})
            game_phase = game_state.get('game_phase', 'unknown')
            
            current_mana = mana_info.get('current_mana', 0)
            playable_cards = self._get_playable_cards(hand_cards, current_mana)
            
            # If it's not our turn, wait
            if game_phase != "my_turn":
                return {'action': 'wait', 'reason': 'Not my turn'}
            
            # If no playable cards, end turn
            if not playable_cards:
                return {'action': 'end_turn', 'reason': 'No playable cards'}
            
            # Decide what to do based on game state
            decision = self._evaluate_game_state(playable_cards, board_state, current_mana)
            
            return decision
            
        except Exception as e:
            self.logger.error(f"Error in decision making: {e}")
            return {'action': 'end_turn', 'reason': 'Error in decision making'}
    
    def _get_playable_cards(self, hand_cards: List[Dict], current_mana: int) -> List[Dict]:
        """Get cards that can be played with current mana"""
        playable = []
        
        for card in hand_cards:
            card_cost = card.get('cost', 0)
            if card_cost <= current_mana:
                playable.append(card)
        
        return playable
    
    def _evaluate_game_state(self, playable_cards: List[Dict], board_state: Dict, current_mana: int) -> Dict:
        """Evaluate the game state and decide on the best move"""
        
        # Get board information
        friendly_minions = board_state.get('friendly_minions', [])
        enemy_minions = board_state.get('enemy_minions', [])
        
        # Calculate board values
        friendly_value = self._calculate_board_value(friendly_minions)
        enemy_value = self._calculate_board_value(enemy_minions)
        
        # Decision logic based on board state
        if enemy_minions and friendly_minions:
            # Both players have minions - consider trading
            return self._decide_trading_strategy(playable_cards, friendly_minions, enemy_minions, current_mana)
        
        elif enemy_minions and not friendly_minions:
            # We have no board presence - play minions or removal
            return self._decide_against_board(playable_cards, enemy_minions, current_mana)
        
        elif not enemy_minions and friendly_minions:
            # We have board control - go face or develop
            return self._decide_with_board_control(playable_cards, friendly_minions, current_mana)
        
        else:
            # Empty board - develop minions
            return self._decide_development(playable_cards, current_mana)
    
    def _decide_trading_strategy(self, playable_cards: List[Dict], friendly_minions: List[Dict], 
                                enemy_minions: List[Dict], current_mana: int) -> Dict:
        """Decide whether to trade or go face"""
        
        # Calculate board values
        friendly_value = self._calculate_board_value(friendly_minions)
        enemy_value = self._calculate_board_value(enemy_minions)
        
        # Look for removal spells
        removal_spells = [card for card in playable_cards if card.get('type') == 'spell']
        
        if removal_spells and enemy_value['total_attack'] > friendly_value['total_health']:
            # Use removal if we're in danger
            best_removal = self._select_best_removal(removal_spells, enemy_minions)
            if best_removal:
                return {
                    'action': 'play_card',
                    'card': best_removal,
                    'target': 'enemy_minion',
                    'reason': 'Removal to protect board'
                }
        
        # Look for minions to play
        minions = [card for card in playable_cards if card.get('type') == 'minion']
        if minions:
            best_minion = self._select_best_minion(minions, current_mana)
            if best_minion:
                return {
                    'action': 'play_card',
                    'card': best_minion,
                    'target': 'board',
                    'reason': 'Develop board presence'
                }
        
        # If no good plays, end turn
        return {'action': 'end_turn', 'reason': 'No optimal plays available'}
    
    def _decide_against_board(self, playable_cards: List[Dict], enemy_minions: List[Dict], current_mana: int) -> Dict:
        """Decide what to do when opponent has board control"""
        
        # Prioritize removal
        removal_spells = [card for card in playable_cards if card.get('type') == 'spell']
        if removal_spells:
            best_removal = self._select_best_removal(removal_spells, enemy_minions)
            if best_removal:
                return {
                    'action': 'play_card',
                    'card': best_removal,
                    'target': 'enemy_minion',
                    'reason': 'Removal to clear opponent board'
                }
        
        # Look for defensive minions
        defensive_minions = [card for card in playable_cards 
                           if card.get('type') == 'minion' and card.get('health', 0) >= 4]
        if defensive_minions:
            best_defensive = self._select_best_minion(defensive_minions, current_mana)
            if best_defensive:
                return {
                    'action': 'play_card',
                    'card': best_defensive,
                    'target': 'board',
                    'reason': 'Play defensive minion'
                }
        
        # Play any minion to contest board
        minions = [card for card in playable_cards if card.get('type') == 'minion']
        if minions:
            best_minion = self._select_best_minion(minions, current_mana)
            if best_minion:
                return {
                    'action': 'play_card',
                    'card': best_minion,
                    'target': 'board',
                    'reason': 'Contest board'
                }
        
        return {'action': 'end_turn', 'reason': 'No good defensive plays'}
    
    def _decide_with_board_control(self, playable_cards: List[Dict], friendly_minions: List[Dict], current_mana: int) -> Dict:
        """Decide what to do when we have board control"""
        
        # Look for buffs or additional minions
        buff_spells = [card for card in playable_cards if self._is_buff_spell(card)]
        if buff_spells and friendly_minions:
            best_buff = self._select_best_buff(buff_spells, friendly_minions)
            if best_buff:
                return {
                    'action': 'play_card',
                    'card': best_buff,
                    'target': 'friendly_minion',
                    'reason': 'Buff existing minions'
                }
        
        # Play additional minions
        minions = [card for card in playable_cards if card.get('type') == 'minion']
        if minions:
            best_minion = self._select_best_minion(minions, current_mana)
            if best_minion:
                return {
                    'action': 'play_card',
                    'card': best_minion,
                    'target': 'board',
                    'reason': 'Develop additional minions'
                }
        
        # Go face with spells
        damage_spells = [card for card in playable_cards if self._is_damage_spell(card)]
        if damage_spells:
            best_damage = self._select_best_damage_spell(damage_spells)
            if best_damage:
                return {
                    'action': 'play_card',
                    'card': best_damage,
                    'target': 'opponent_face',
                    'reason': 'Go face with spell'
                }
        
        return {'action': 'end_turn', 'reason': 'No good offensive plays'}
    
    def _decide_development(self, playable_cards: List[Dict], current_mana: int) -> Dict:
        """Decide what to do on an empty board"""
        
        # Play the best minion available
        minions = [card for card in playable_cards if card.get('type') == 'minion']
        if minions:
            best_minion = self._select_best_minion(minions, current_mana)
            if best_minion:
                return {
                    'action': 'play_card',
                    'card': best_minion,
                    'target': 'board',
                    'reason': 'Develop board presence'
                }
        
        # Play utility spells
        utility_spells = [card for card in playable_cards if card.get('type') == 'spell']
        if utility_spells:
            best_utility = self._select_best_utility_spell(utility_spells)
            if best_utility:
                return {
                    'action': 'play_card',
                    'card': best_utility,
                    'target': 'self',
                    'reason': 'Play utility spell'
                }
        
        return {'action': 'end_turn', 'reason': 'No good development plays'}
    
    def _select_best_minion(self, minions: List[Dict], current_mana: int) -> Optional[Dict]:
        """Select the best minion to play"""
        if not minions:
            return None
        
        # Score minions based on various factors
        scored_minions = []
        for minion in minions:
            score = 0
            
            # Prefer higher attack/health ratio
            attack = minion.get('attack', 0)
            health = minion.get('health', 0)
            if health > 0:
                score += (attack / health) * 10
            
            # Prefer minions that use most of our mana
            cost = minion.get('cost', 0)
            if cost > 0:
                score += (cost / current_mana) * 20
            
            # Bonus for taunt minions
            if 'taunt' in minion.get('description', '').lower():
                score += 5
            
            scored_minions.append((minion, score))
        
        # Return the highest scored minion
        scored_minions.sort(key=lambda x: x[1], reverse=True)
        return scored_minions[0][0] if scored_minions else None
    
    def _select_best_removal(self, removal_spells: List[Dict], enemy_minions: List[Dict]) -> Optional[Dict]:
        """Select the best removal spell"""
        if not removal_spells:
            return None
        
        # For now, return the first removal spell
        # In a more sophisticated version, you'd consider damage vs minion health
        return removal_spells[0]
    
    def _select_best_buff(self, buff_spells: List[Dict], friendly_minions: List[Dict]) -> Optional[Dict]:
        """Select the best buff spell"""
        if not buff_spells:
            return None
        
        return buff_spells[0]
    
    def _select_best_damage_spell(self, damage_spells: List[Dict]) -> Optional[Dict]:
        """Select the best damage spell"""
        if not damage_spells:
            return None
        
        # Prefer higher damage spells
        return max(damage_spells, key=lambda x: x.get('damage', 0), default=damage_spells[0])
    
    def _select_best_utility_spell(self, utility_spells: List[Dict]) -> Optional[Dict]:
        """Select the best utility spell"""
        if not utility_spells:
            return None
        
        return utility_spells[0]
    
    def _calculate_board_value(self, minions: List[Dict]) -> Dict:
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
    
    def _is_buff_spell(self, card: Dict) -> bool:
        """Check if a spell is a buff spell"""
        description = card.get('description', '').lower()
        buff_keywords = ['give', 'gain', '+', 'buff', 'enchant']
        return any(keyword in description for keyword in buff_keywords)
    
    def _is_damage_spell(self, card: Dict) -> bool:
        """Check if a spell is a damage spell"""
        description = card.get('description', '').lower()
        damage_keywords = ['deal', 'damage', 'destroy']
        return any(keyword in description for keyword in damage_keywords) 