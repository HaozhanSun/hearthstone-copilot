import json
import os
from typing import Dict, List, Optional


class CardDatabase:
    """Database for storing and looking up Hearthstone card information"""
    
    def __init__(self, database_path: str = "card_database.json"):
        self.database_path = database_path
        self.cards = {}
        self.load_database()
    
    def load_database(self):
        """Load card database from file"""
        if os.path.exists(self.database_path):
            try:
                with open(self.database_path, 'r', encoding='utf-8') as f:
                    self.cards = json.load(f)
            except Exception as e:
                print(f"Error loading card database: {e}")
                self.cards = {}
        else:
            # Initialize with some basic cards
            self.cards = self.get_default_cards()
            self.save_database()
    
    def save_database(self):
        """Save card database to file"""
        try:
            with open(self.database_path, 'w', encoding='utf-8') as f:
                json.dump(self.cards, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving card database: {e}")
    
    def get_default_cards(self) -> Dict:
        """Get default card database with common cards"""
        return {
            "Fireball": {
                "name": "Fireball",
                "cost": 4,
                "type": "spell",
                "rarity": "common",
                "class": "mage",
                "description": "Deal 6 damage."
            },
            "Frostbolt": {
                "name": "Frostbolt",
                "cost": 2,
                "type": "spell",
                "rarity": "common",
                "class": "mage",
                "description": "Deal 3 damage to a character and Freeze it."
            },
            "Arcane Intellect": {
                "name": "Arcane Intellect",
                "cost": 3,
                "type": "spell",
                "rarity": "common",
                "class": "mage",
                "description": "Draw 2 cards."
            },
            "Water Elemental": {
                "name": "Water Elemental",
                "cost": 4,
                "type": "minion",
                "rarity": "common",
                "class": "mage",
                "attack": 3,
                "health": 6,
                "description": "Freeze any character damaged by this minion."
            },
            "Polymorph": {
                "name": "Polymorph",
                "cost": 4,
                "type": "spell",
                "rarity": "common",
                "class": "mage",
                "description": "Transform a minion into a 1/1 Sheep."
            },
            "Flamestrike": {
                "name": "Flamestrike",
                "cost": 7,
                "type": "spell",
                "rarity": "common",
                "class": "mage",
                "description": "Deal 4 damage to all enemy minions."
            },
            "Kobold Geomancer": {
                "name": "Kobold Geomancer",
                "cost": 2,
                "type": "minion",
                "rarity": "common",
                "class": "neutral",
                "attack": 2,
                "health": 2,
                "description": "Spell Damage +1"
            },
            "Chillwind Yeti": {
                "name": "Chillwind Yeti",
                "cost": 4,
                "type": "minion",
                "rarity": "common",
                "class": "neutral",
                "attack": 4,
                "health": 5,
                "description": ""
            },
            "Sen'jin Shieldmasta": {
                "name": "Sen'jin Shieldmasta",
                "cost": 4,
                "type": "minion",
                "rarity": "common",
                "class": "neutral",
                "attack": 3,
                "health": 5,
                "description": "Taunt"
            },
            "Boulderfist Ogre": {
                "name": "Boulderfist Ogre",
                "cost": 6,
                "type": "minion",
                "rarity": "common",
                "class": "neutral",
                "attack": 6,
                "health": 7,
                "description": ""
            }
        }
    
    def add_card(self, card_info: Dict):
        """Add a card to the database"""
        if 'name' in card_info:
            self.cards[card_info['name']] = card_info
            self.save_database()
    
    def get_card(self, card_name: str) -> Optional[Dict]:
        """Get card information by name"""
        return self.cards.get(card_name)
    
    def search_cards(self, query: str) -> List[Dict]:
        """Search for cards by name (partial match)"""
        query = query.lower()
        results = []
        
        for card_name, card_info in self.cards.items():
            if query in card_name.lower():
                results.append(card_info)
        
        return results
    
    def get_cards_by_cost(self, cost: int) -> List[Dict]:
        """Get all cards with a specific mana cost"""
        return [card for card in self.cards.values() if card.get('cost') == cost]
    
    def get_cards_by_type(self, card_type: str) -> List[Dict]:
        """Get all cards of a specific type"""
        return [card for card in self.cards.values() if card.get('type') == card_type]
    
    def get_cards_by_class(self, card_class: str) -> List[Dict]:
        """Get all cards of a specific class"""
        return [card for card in self.cards.values() if card.get('class') == card_class]
    
    def get_all_card_names(self) -> List[str]:
        """Get list of all card names in database"""
        return list(self.cards.keys())
    
    def fuzzy_match_card(self, card_name: str, threshold: float = 0.8) -> Optional[str]:
        """Fuzzy match card name (for OCR errors)"""
        from difflib import SequenceMatcher
        
        card_name_lower = card_name.lower()
        best_match = None
        best_ratio = 0
        
        for db_card_name in self.cards.keys():
            ratio = SequenceMatcher(None, card_name_lower, db_card_name.lower()).ratio()
            if ratio > best_ratio and ratio >= threshold:
                best_ratio = ratio
                best_match = db_card_name
        
        return best_match
    
    def get_card_synergies(self, card_name: str) -> List[str]:
        """Get cards that synergize well with the given card"""
        # This is a simplified version - would need more sophisticated logic
        card = self.get_card(card_name)
        if not card:
            return []
        
        synergies = []
        
        # Example synergies based on card type and class
        if card.get('type') == 'spell' and card.get('class') == 'mage':
            # Spell damage synergies
            synergies.extend(['Kobold Geomancer', 'Dalaran Mage'])
        
        return synergies
    
    def get_optimal_play_order(self, hand_cards: List[str], mana: int) -> List[str]:
        """Get optimal play order for cards in hand"""
        # Simple algorithm: play highest cost cards first if mana allows
        available_cards = []
        
        for card_name in hand_cards:
            card = self.get_card(card_name)
            if card and card.get('cost', 0) <= mana:
                available_cards.append((card_name, card.get('cost', 0)))
        
        # Sort by cost (highest first)
        available_cards.sort(key=lambda x: x[1], reverse=True)
        
        return [card_name for card_name, _ in available_cards] 