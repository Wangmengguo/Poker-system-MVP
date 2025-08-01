from typing import List, Any, Optional
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from l1_domain.game_state import GameState, Player, Position, PlayerStatus, GameConfig
from l1_domain.action import Action, ActionType, FoldAction, CallAction, CheckAction, RaiseAction, AllInAction
from l1_domain.translator import Translator, GameEngine, StepResult
from l1_domain.rules import PokerRules

try:
    from pokerkit import NoLimitTexasHoldem, Automation
    from pokerkit.utilities import Card
    POKERKIT_AVAILABLE = True
except ImportError:
    POKERKIT_AVAILABLE = False
    print("Warning: PokerKit not installed. Install with: pip install pokerkit==0.6.3")


class PokerKitExecutor(GameEngine):
    """Minimal wrapper around PokerKit implementing the Translator protocol"""
    
    def __init__(self):
        if not POKERKIT_AVAILABLE:
            raise ImportError("PokerKit is required but not installed")
        self.current_pk_state = None
    
    def create_initial_state(self, config: GameConfig) -> GameState:
        """Create initial game state from configuration"""
        starting_stacks = [config.starting_stack] * config.num_players
        
        self.current_pk_state = NoLimitTexasHoldem.create_state(
            automations=(
                Automation.ANTE_POSTING,
                Automation.BET_COLLECTION,
                Automation.BLIND_OR_STRADDLE_POSTING,
                Automation.HOLE_DEALING,
                Automation.BOARD_DEALING,
                Automation.CARD_BURNING,
                Automation.HAND_KILLING,
                Automation.CHIPS_PUSHING,
                Automation.CHIPS_PULLING,
            ),
            ante_trimming_status=False,
            raw_antes=(),
            raw_blinds_or_straddles=(config.small_blind, config.big_blind),
            min_bet=config.big_blind,
            raw_starting_stacks=starting_stacks,
            player_count=config.num_players,
        )
        
        return self.from_engine_state(self.current_pk_state)
    
    def to_engine_state(self, game_state: GameState) -> Any:
        """Convert L1 GameState to PokerKit State"""
        return self.current_pk_state
    
    def from_engine_state(self, pk_state: Any) -> GameState:
        """Convert PokerKit State to L1 GameState"""
        players = []
        
        for i in range(pk_state.player_count):
            hole_cards = None
            if pk_state.hole_cards and i < len(pk_state.hole_cards) and pk_state.hole_cards[i]:
                hole_cards = tuple([str(card) for card in pk_state.hole_cards[i]])
            
            status = PlayerStatus.ACTIVE
            if i < len(pk_state.statuses) and not pk_state.statuses[i]:  # Player is out
                status = PlayerStatus.OUT
            
            current_bet = pk_state.bets[i] if i < len(pk_state.bets) else 0
            
            player = Player(
                id=f"Player_{i}",
                stack=pk_state.stacks[i],
                hole_cards=hole_cards,
                position=self._get_position(i, pk_state.player_count),
                status=status,
                current_bet=current_bet,
                total_bet_this_hand=current_bet  # Simplified for MVP
            )
            players.append(player)
        
        community_cards = tuple([str(card) for card in pk_state.board_cards]) if pk_state.board_cards else tuple()
        
        current_player_index = 0
        if pk_state.actor_index is not None:
            current_player_index = pk_state.actor_index
        
        street = self._get_street_name(pk_state)
        
        # Get blinds from blinds_or_straddles tuple
        small_blind = pk_state.blinds_or_straddles[0] if pk_state.blinds_or_straddles else 0
        big_blind = pk_state.blinds_or_straddles[1] if len(pk_state.blinds_or_straddles) > 1 else 0
        
        return GameState(
            players=tuple(players),
            community_cards=community_cards,
            pot=sum(pk_state.bets) if pk_state.bets else 0,
            current_player_index=current_player_index,
            dealer_index=0,  # Simplified for MVP
            small_blind=small_blind,
            big_blind=big_blind,
            current_bet=max(pk_state.bets) if pk_state.bets else 0,
            street=street,
            is_terminal=not pk_state.status,
            winner_index=self._determine_winner_via_l1_rules(pk_state),
        )
    
    def to_engine_action(self, action: Action, game_state: GameState) -> Any:
        """Convert L1 Action to PokerKit action"""
        if isinstance(action, FoldAction):
            return "fold"
        elif isinstance(action, CheckAction):
            return "check"
        elif isinstance(action, CallAction):
            return "call"
        elif isinstance(action, RaiseAction):
            return f"raise {action.amount}"
        elif isinstance(action, AllInAction):
            current_player = game_state.current_player
            return f"raise {current_player.stack}"
        else:
            raise ValueError(f"Unknown action type: {type(action)}")
    
    def get_legal_actions(self, game_state: GameState) -> List[str]:
        """Get list of legal action strings for current player"""
        if not self.current_pk_state:
            return []
        
        actions = []
        current_player = game_state.current_player
        current_bet = game_state.current_bet
        player_bet = current_player.current_bet
        
        # Always can fold (unless already all-in)
        if current_player.stack > 0:
            actions.append("f")
        
        # Can check if no bet to call
        if current_bet == player_bet:
            actions.append("ch")
        
        # Can call if there's a bet and player has chips
        if current_bet > player_bet and current_player.stack >= (current_bet - player_bet):
            actions.append("c")
        
        # Can raise if has chips
        if current_player.stack > 0:
            actions.append("r <amount>")
            actions.append("a")  # all-in
        
        return actions
    
    def step(self, game_state: GameState, action: Action) -> StepResult:
        """Execute one action and return new state"""
        if not self.current_pk_state:
            raise ValueError("No active PokerKit state")
        
        # Convert action to PokerKit format
        pk_action = self.to_engine_action(action, game_state)
        
        # Execute action in PokerKit
        try:
            if isinstance(action, FoldAction):
                self.current_pk_state.fold()
            elif isinstance(action, CheckAction):
                self.current_pk_state.check_or_call()
            elif isinstance(action, CallAction):
                self.current_pk_state.check_or_call()
            elif isinstance(action, RaiseAction):
                total_amount = action.amount + game_state.current_player.current_bet
                self.current_pk_state.complete_bet_or_raise_to(total_amount)
            elif isinstance(action, AllInAction):
                current_player = game_state.current_player
                total_amount = current_player.current_bet + current_player.stack
                self.current_pk_state.complete_bet_or_raise_to(total_amount)
            
        except Exception as e:
            print(f"PokerKit action failed: {e}")
            # Return current state if action fails
            return StepResult(game_state, [], game_state.is_terminal)
        
        # Convert back to L1 state
        new_game_state = self.from_engine_state(self.current_pk_state)
        
        events = [f"{action.player_id} performed {action.action_type.value}"]
        
        return StepResult(new_game_state, events, new_game_state.is_terminal)
    
    def _get_position(self, player_index: int, num_players: int) -> Position:
        """Map player index to position"""
        if num_players < 2:
            return Position.BUTTON
        elif num_players == 2:
            return Position.SMALL_BLIND if player_index == 0 else Position.BIG_BLIND
        else:
            # Simplified position mapping for MVP
            if player_index == 0:
                return Position.SMALL_BLIND
            elif player_index == 1:
                return Position.BIG_BLIND
            elif player_index == num_players - 1:
                return Position.BUTTON
            elif player_index == num_players - 2:
                return Position.CUTOFF
            else:
                return Position.MIDDLE_POSITION
    
    def _get_street_name(self, pk_state: Any) -> str:
        """Map PokerKit street to string"""
        if not hasattr(pk_state, 'street') or pk_state.street is None:
            return "preflop"
        
        street_names = {
            0: "preflop",
            1: "flop", 
            2: "turn",
            3: "river"
        }
        return street_names.get(pk_state.street, "preflop")
    
    def _determine_winner_via_l1_rules(self, pk_state: Any) -> Optional[int]:
        """
        Determine winner by translating to L1 state and calling L1 rules
        L2 ONLY does translation - L1 contains all poker logic
        """
        try:
            # If game is still running, no winner yet
            if pk_state.status:
                return None
            
            # Create temporary L1 state WITHOUT calling from_engine_state to avoid recursion
            temp_l1_state = self._create_temp_l1_state_for_winner_check(pk_state)
            
            # Call L1 pure rules to determine winner
            winners, payouts = PokerRules.determine_winners(temp_l1_state)
            
            # Return first winner (MVP simplification)
            return winners[0] if winners else None
            
        except Exception as e:
            print(f"Warning: Could not determine winner via L1 rules: {e}")
            return None
    
    def _create_temp_l1_state_for_winner_check(self, pk_state: Any) -> GameState:
        """Create temporary L1 state for winner determination - avoids recursion"""
        players = []
        
        for i in range(pk_state.player_count):
            hole_cards = None
            if pk_state.hole_cards and i < len(pk_state.hole_cards) and pk_state.hole_cards[i]:
                hole_cards = tuple([str(card) for card in pk_state.hole_cards[i]])
            
            status = PlayerStatus.ACTIVE
            if i < len(pk_state.statuses) and not pk_state.statuses[i]:  # Player is out
                status = PlayerStatus.OUT
            
            current_bet = pk_state.bets[i] if i < len(pk_state.bets) else 0
            
            player = Player(
                id=f"Player_{i}",
                stack=pk_state.stacks[i],
                hole_cards=hole_cards,
                position=self._get_position(i, pk_state.player_count),
                status=status,
                current_bet=current_bet,
                total_bet_this_hand=current_bet
            )
            players.append(player)
        
        community_cards = tuple([str(card) for card in pk_state.board_cards]) if pk_state.board_cards else tuple()
        street = self._get_street_name(pk_state)
        
        return GameState(
            players=tuple(players),
            community_cards=community_cards,
            pot=sum(pk_state.bets) if pk_state.bets else 0,
            current_player_index=0,  # Not needed for winner determination
            dealer_index=0,
            small_blind=pk_state.blinds_or_straddles[0] if pk_state.blinds_or_straddles else 0,
            big_blind=pk_state.blinds_or_straddles[1] if len(pk_state.blinds_or_straddles) > 1 else 0,
            current_bet=max(pk_state.bets) if pk_state.bets else 0,
            street=street,
            is_terminal=not pk_state.status,
            winner_index=None  # Will be determined by L1 rules
        )