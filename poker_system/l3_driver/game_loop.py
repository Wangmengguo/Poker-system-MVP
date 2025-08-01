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

    def export_hand_history(self, filename: str = None) -> str:
        """Export hand history with comprehensive data"""
        import json
        from datetime import datetime
        
        # Generate comprehensive hand data
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "game_type": "No-Limit Texas Hold'em",
            "version": "1.0.0-MVP",
            "hand_history": self.hand_history,
            "final_state": None,
            "winner_analysis": None,
            "statistics": None
        }
        
        if self.current_state:
            # Export final game state
            export_data["final_state"] = {
                "players": [
                    {
                        "id": p.id,
                        "final_stack": p.stack,
                        "position": p.position.value if p.position else None,
                        "status": p.status.value,
                        "hole_cards": p.hole_cards if p.hole_cards else None
                    }
                    for p in self.current_state.players
                ],
                "community_cards": list(self.current_state.community_cards),
                "pot": self.current_state.pot,
                "street": self.current_state.street,
                "is_terminal": self.current_state.is_terminal
            }
            
            # Enhanced winner analysis (will use L1 rules after Track 1 merge)
            if self.current_state.is_terminal and self.current_state.winner_index is not None:
                winner = self.current_state.players[self.current_state.winner_index]
                export_data["winner_analysis"] = {
                    "winner_index": self.current_state.winner_index,
                    "winner_id": winner.id,
                    "winner_final_stack": winner.stack,
                    "winning_method": "L1_rules_evaluation",  # Will be accurate after Track 1
                    "pot_won": self.current_state.pot
                }
            
            # Generate basic statistics
            export_data["statistics"] = self.get_game_statistics()
        
        # Convert to JSON
        json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(json_str)
                return f"Hand history exported to {filename}"
            except IOError as e:
                return f"Failed to export to {filename}: {e}"
        
        return json_str

    def get_game_statistics(self) -> dict:
        """Get comprehensive game statistics"""
        stats = {
            "players": {},
            "game_summary": {},
            "action_summary": {}
        }
        
        if not self.current_state:
            return stats
        
        # Game summary statistics
        stats["game_summary"] = {
            "total_pot": self.current_state.pot,
            "final_street": self.current_state.street,
            "is_complete": self.current_state.is_terminal,
            "num_players": len(self.current_state.players),
            "total_actions": len(self.hand_history) - 1  # Exclude game start message
        }
        
        # Player statistics
        for i, player in enumerate(self.current_state.players):
            stats["players"][player.id] = {
                "final_stack": player.stack,
                "position": player.position.value if player.position else None,
                "status": player.status.value,
                "is_winner": (self.current_state.winner_index == i),
                "stack_change": player.stack - stats["game_summary"].get("starting_stack", 1000),
                "current_bet": player.current_bet,
                "total_bet_this_hand": player.total_bet_this_hand
            }
            
            # Calculate winnings/losses
            if self.current_state.is_terminal and self.current_state.winner_index == i:
                stats["players"][player.id]["winnings"] = self.current_state.pot
            else:
                stats["players"][player.id]["winnings"] = 0
        
        # Action summary (basic analysis of hand history)
        action_counts = {}
        for event in self.hand_history:
            if any(action in event.lower() for action in ['fold', 'call', 'raise', 'check', 'all-in']):
                for action_type in ['fold', 'call', 'raise', 'check', 'all-in']:
                    if action_type in event.lower():
                        action_counts[action_type] = action_counts.get(action_type, 0) + 1
                        break
        
        stats["action_summary"] = action_counts
        
        return stats

    def display_game_summary(self):
        """Display a formatted game summary"""
        if not self.current_state:
            return
            
        print("\n" + "="*50)
        print("GAME SUMMARY")
        print("="*50)
        
        # Winner information
        if self.current_state.is_terminal and self.current_state.winner_index is not None:
            winner = self.current_state.players[self.current_state.winner_index]
            print(f"🏆 WINNER: {winner.id}")
            print(f"💰 Pot Won: ${self.current_state.pot}")
            print(f"📊 Final Stack: ${winner.stack}")
        
        # Final stacks
        print("\nFinal Stacks:")
        for player in self.current_state.players:
            status_icon = "🏆" if (self.current_state.winner_index is not None and 
                                self.current_state.players[self.current_state.winner_index].id == player.id) else "💰"
            print(f"  {status_icon} {player.id}: ${player.stack}")
        
        # Game statistics
        stats = self.get_game_statistics()
        print(f"\nGame Stats:")
        print(f"  Total Actions: {stats['game_summary']['total_actions']}")
        print(f"  Final Street: {stats['game_summary']['final_street'].title()}")
        print(f"  Total Pot: ${stats['game_summary']['total_pot']}")
        
        # Action summary
        if stats["action_summary"]:
            print(f"\nAction Summary:")
            for action, count in stats["action_summary"].items():
                print(f"  {action.title()}s: {count}")

    def prompt_for_export(self) -> bool:
        """Prompt user for hand history export"""
        if not self.current_state or not self.current_state.is_terminal:
            return False
            
        try:
            choice = input("\n📁 Export hand history? (y/N): ").strip().lower()
            if choice in ['y', 'yes']:
                import time
                filename = f"hand_history_{int(time.time())}.json"
                result = self.export_hand_history(filename)
                print(f"✅ {result}")
                return True
        except (KeyboardInterrupt, EOFError):
            print("\nSkipping export.")
        
        return False