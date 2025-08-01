import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from typing import Callable, Optional, List
from l1_domain.game_state import GameState, GameConfig
from l1_domain.action import Action, parse_action
from l1_domain.translator import GameEngine, StepResult


class GameLoop:
    """L3 Driver: Manages the main game loop and flow control"""
    
    def __init__(self, engine: GameEngine):
        self.engine = engine
        self.current_state: Optional[GameState] = None
        self.hand_history: List[str] = []
    
    def start_game(self, config: GameConfig) -> GameState:
        """Initialize a new game with the given configuration"""
        self.current_state = self.engine.create_initial_state(config)
        self.hand_history = []
        self.hand_history.append(f"Game started: {config.num_players} players, ${config.small_blind}/${config.big_blind} blinds")
        return self.current_state
    
    def run_game_loop(self, 
                     get_player_action: Callable[[GameState, List[str]], str],
                     display_state: Callable[[GameState], None],
                     display_message: Callable[[str], None]) -> GameState:
        """
        Main game loop
        
        Args:
            get_player_action: Function to get action input from current player
            display_state: Function to display current game state
            display_message: Function to display messages
        """
        if not self.current_state:
            raise ValueError("Game not started. Call start_game() first.")
        
        while not self.current_state.is_terminal:
            # Display current state
            display_state(self.current_state)
            
            # Get legal actions for current player
            legal_actions = self.engine.get_legal_actions(self.current_state)
            
            # Get player input
            current_player = self.current_state.current_player
            display_message(f"\n{current_player.id}'s turn. Legal actions: {', '.join(legal_actions)}")
            
            action_str = get_player_action(self.current_state, legal_actions)
            
            # Parse action
            action = parse_action(action_str, current_player.id)
            if not action:
                display_message(f"Invalid action: {action_str}. Try again.")
                continue
            
            # Validate action
            if not self._is_action_valid(action, self.current_state):
                display_message(f"Invalid action: {action_str}. Try again.")
                continue
            
            # Execute action
            try:
                step_result = self.engine.step(self.current_state, action)
                self.current_state = step_result.game_state
                
                # Log the action
                action_log = f"{action.player_id} {action.action_type.value}"
                if hasattr(action, 'amount'):
                    action_log += f" {action.amount}"
                self.hand_history.append(action_log)
                
                # Display any events
                for event in step_result.events:
                    display_message(event)
                
                if step_result.is_terminal:
                    display_message("\nHand complete!")
                    break
                    
            except Exception as e:
                display_message(f"Error executing action: {e}")
                continue
        
        # Display final state
        display_state(self.current_state)
        self._display_results(display_message)
        
        return self.current_state
    
    def _is_action_valid(self, action: Action, game_state: GameState) -> bool:
        """Basic action validation"""
        current_player = game_state.current_player
        return action.is_valid(
            game_state.current_bet,
            current_player.stack,
            current_player.current_bet
        )
    
    def _display_results(self, display_message: Callable[[str], None]):
        """Display game results"""
        if not self.current_state:
            return
        
        display_message("\n" + "="*50)
        display_message("GAME RESULTS")
        display_message("="*50)
        
        # Show final stacks
        for player in self.current_state.players:
            display_message(f"{player.id}: ${player.stack}")
        
        # Show hand history
        display_message("\nHand History:")
        for event in self.hand_history:
            display_message(f"  {event}")
    
    def get_hand_history(self) -> List[str]:
        """Get the complete hand history"""
        return self.hand_history.copy()
    
    def reset_game(self):
        """Reset the game state"""
        self.current_state = None
        self.hand_history = []