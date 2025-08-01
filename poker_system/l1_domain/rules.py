from typing import List, Tuple, Optional, Dict
from enum import Enum
from .game_state import GameState, Player, PlayerStatus
from .action import Action


class HandRank(Enum):
    """Standard poker hand rankings"""
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10


class PokerRules:
    """Pure poker rules - engine agnostic"""
    
    @staticmethod
    def evaluate_hand(hole_cards: Tuple[str, str], community_cards: Tuple[str, ...]) -> Tuple[HandRank, List[str]]:
        """
        Evaluate 5-card poker hand strength
        Returns: (hand_rank, kickers) for comparison
        """
        if not hole_cards or len(community_cards) < 3:
            return HandRank.HIGH_CARD, []
        
        # For MVP: simplified evaluation
        # TODO: Implement full hand evaluation
        all_cards = list(hole_cards) + list(community_cards)
        return HandRank.HIGH_CARD, all_cards[:5]
    
    @staticmethod
    def compare_hands(hand1: Tuple[HandRank, List[str]], hand2: Tuple[HandRank, List[str]]) -> int:
        """
        Compare two poker hands
        Returns: 1 if hand1 wins, -1 if hand2 wins, 0 if tie
        """
        rank1, kickers1 = hand1
        rank2, kickers2 = hand2
        
        if rank1.value > rank2.value:
            return 1
        elif rank1.value < rank2.value:
            return -1
        else:
            # Same rank, compare kickers (simplified for MVP)
            return 0
    
    @staticmethod
    def determine_winners(state: GameState) -> Tuple[List[int], Dict[int, int]]:
        """
        Determine winners and calculate payouts - PURE POKER LOGIC
        
        Args:
            state: Complete game state with all player information
            
        Returns:
            (winner_indices, payouts) where payouts[player_idx] = amount_won
        """
        if not state.is_terminal:
            return [], {}
        
        # Find active players (not folded)
        active_players = []
        for i, player in enumerate(state.players):
            if player.status == PlayerStatus.ACTIVE:
                active_players.append(i)
        
        # Case 1: Only one active player (others folded)
        if len(active_players) == 1:
            winner_idx = active_players[0]
            return [winner_idx], {winner_idx: state.pot}
        
        # Case 2: Showdown required
        if len(active_players) > 1:
            return PokerRules._evaluate_showdown(state, active_players)
        
        # Case 3: No active players (shouldn't happen)
        return [], {}
    
    @staticmethod
    def _evaluate_showdown(state: GameState, active_players: List[int]) -> Tuple[List[int], Dict[int, int]]:
        """Evaluate showdown between active players"""
        if len(state.community_cards) < 5:
            # Pre-river: simplified logic for MVP
            # TODO: Implement proper showdown for all streets
            return [active_players[0]], {active_players[0]: state.pot}
        
        # Evaluate all hands
        hands = {}
        for player_idx in active_players:
            player = state.players[player_idx]
            if player.hole_cards:
                hand_strength = PokerRules.evaluate_hand(player.hole_cards, state.community_cards)
                hands[player_idx] = hand_strength
        
        if not hands:
            return [], {}
        
        # Find best hand(s)
        best_players = []
        best_hand = None
        
        for player_idx, hand in hands.items():
            if best_hand is None:
                best_hand = hand
                best_players = [player_idx]
            else:
                comparison = PokerRules.compare_hands(hand, best_hand)
                if comparison > 0:  # New best hand
                    best_hand = hand
                    best_players = [player_idx]
                elif comparison == 0:  # Tie
                    best_players.append(player_idx)
        
        # Distribute pot among winners
        payout_per_winner = state.pot // len(best_players)
        payouts = {player_idx: payout_per_winner for player_idx in best_players}
        
        return best_players, payouts
    
    @staticmethod
    def is_game_complete(state: GameState) -> bool:
        """Check if game/hand is complete"""
        active_count = sum(1 for p in state.players if p.status == PlayerStatus.ACTIVE)
        return active_count <= 1 or state.street == "river"  # Simplified for MVP
    
    @staticmethod
    def get_next_street(current_street: str) -> Optional[str]:
        """Get next betting street"""
        streets = ["preflop", "flop", "turn", "river"]
        try:
            current_idx = streets.index(current_street)
            return streets[current_idx + 1] if current_idx < len(streets) - 1 else None
        except ValueError:
            return None