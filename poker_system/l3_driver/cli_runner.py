import sys
import os
from typing import List, Dict, Any

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from l1_domain.game_state import GameState, GameConfig, PlayerStatus
from l2_executor.pokerkit_executor import PokerKitExecutor
from l3_driver.game_loop import GameLoop


class PokerCLI:
    """CLI game runner in L3 for proper separation"""
    
    def __init__(self):
        self.executor = PokerKitExecutor()
        self.game_loop = GameLoop(self.executor)
    
    def display_state(self, state: GameState):
        """Display current game state with enhanced formatting"""
        print("\n" + "="*60)
        print(f"STREET: {state.street.upper()}")
        print(f"POT: ${state.pot}")
        print(f"CURRENT BET: ${state.current_bet}")
        print("="*60)
        
        # Show community cards with better formatting
        if state.community_cards:
            cards_display = " ".join(state.community_cards)
            print(f"COMMUNITY CARDS: {cards_display}")
        else:
            print("COMMUNITY CARDS: (none)")
        
        print("\nPLAYERS:")
        print("-" * 60)
        
        for i, player in enumerate(state.players):
            # Indicate current player
            indicator = "→" if i == state.current_player_index else " "
            status_str = f"[{player.status.value.upper()}]"
            
            # Show hole cards if available
            hole_cards_str = ""
            if player.hole_cards:
                hole_cards_str = f" Cards: {' '.join(player.hole_cards)}"
            
            # Show position
            position_str = f"({player.position.value})" if player.position else ""
            
            print(f"{indicator} {player.id} {position_str} {status_str}")
            print(f"   Stack: ${player.stack} | Current Bet: ${player.current_bet}{hole_cards_str}")
        
        print("-" * 60)
    
    def display_message(self, message: str):
        """Display a message with consistent formatting"""
        print(message)
    
    def get_player_action(self, state: GameState, legal_actions: List[str]) -> str:
        """Get action input from current player with help"""
        current_player = state.current_player
        print(f"\nAvailable actions: {', '.join(legal_actions)}")
        print("Commands: f=fold, c=call, ch=check, r <amount>=raise, a=all-in")
        
        while True:
            try:
                action = input(f"{current_player.id}, enter your action: ").strip()
                if action:
                    return action
                print("Please enter an action.")
            except (KeyboardInterrupt, EOFError):
                print("\nExiting game...")
                sys.exit(0)
    
    def run_single_game(self, config: GameConfig):
        """Run a complete poker game with proper winner display"""
        print(f"\nStarting {config.num_players}-player No-Limit Texas Hold'em")
        print(f"Blinds: ${config.small_blind}/${config.big_blind}")
        print(f"Starting stacks: ${config.starting_stack}")
        print("\nType Ctrl+C to quit during the game.")
        
        try:
            # Start the game
            initial_state = self.game_loop.start_game(config)
            
            # Run the main game loop
            final_state = self.game_loop.run_game_loop(
                get_player_action=self.get_player_action,
                display_state=self.display_state,
                display_message=self.display_message
            )
            
            # Enhanced winner display (will be fully functional after Track 1 merge)
            if final_state and final_state.winner_index is not None:
                winner = final_state.players[final_state.winner_index]
                print(f"\n🏆 WINNER: {winner.id} with ${winner.stack}!")
                
                # Show final chip counts
                print("\nFinal Chip Counts:")
                for player in final_state.players:
                    status_icon = "🏆" if player.id == winner.id else "💰"
                    print(f"  {status_icon} {player.id}: ${player.stack}")
            else:
                print("\nGame ended without a clear winner.")
            
            # Display enhanced game summary
            self.game_loop.display_game_summary()

            # Prompt for export
            if final_state and final_state.is_terminal:
                self.game_loop.prompt_for_export()

            print("\nGame completed successfully!")
            return final_state
            
        except KeyboardInterrupt:
            print("\n\nGame interrupted by user.")
            return None
        except Exception as e:
            print(f"\nGame error: {e}")
            import traceback
            traceback.print_exc()
            return None


def run_cli(config_dict: Dict[str, Any]) -> None:
    """Main CLI entry point called from L5"""
    try:
        # Extract and validate configuration
        players = config_dict.get('players', 3)
        sb = config_dict.get('sb', 10)
        bb = config_dict.get('bb', 20)
        stack = config_dict.get('stack', 1000)
        
        # Enhanced validation with better error messages
        if not (2 <= players <= 9):
            print("❌ Error: Number of players must be between 2 and 9")
            print(f"   You specified: {players} players")
            return
        
        if sb <= 0 or bb <= 0:
            print("❌ Error: Blinds must be positive numbers")
            print(f"   You specified: SB=${sb}, BB=${bb}")
            return
            
        if bb <= sb:
            print("❌ Error: Big blind must be larger than small blind")
            print(f"   You specified: SB=${sb}, BB=${bb}")
            return
        
        if stack <= bb * 2:
            print("❌ Error: Starting stack must be at least 2x the big blind")
            print(f"   You specified: Stack=${stack}, BB=${bb}")
            print(f"   Minimum required: ${bb * 2}")
            return
        
        # Create and validate configuration
        config = GameConfig(players, sb, bb, stack)
        
        # Display configuration summary
        print("🎮 Game Configuration:")
        print(f"   Players: {config.num_players}")
        print(f"   Blinds: ${config.small_blind}/${config.big_blind}")
        print(f"   Starting Stack: ${config.starting_stack}")
        
        # Run the game
        cli = PokerCLI()
        cli.run_single_game(config)
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print("Please check your parameters and try again.")


def run_cli_with_history_export(config_dict: Dict[str, Any]) -> None:
    """Extended CLI runner with export functionality (Step 5 integration)"""
    # First run the normal game
    run_cli(config_dict)
    
    # TODO: This will be enhanced in Step 5 with export functionality