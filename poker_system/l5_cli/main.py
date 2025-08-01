#!/usr/bin/env python3
"""
L5 CLI Layer: Minimal CLI interface for the poker system MVP
"""

import sys
import os
import argparse
from typing import List

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from l1_domain.game_state import GameState, GameConfig, PlayerStatus
from l2_executor.pokerkit_executor import PokerKitExecutor
from l3_driver.game_loop import GameLoop


class PokerCLI:
    """Simple CLI interface for poker game"""
    
    def __init__(self):
        self.executor = PokerKitExecutor()
        self.game_loop = GameLoop(self.executor)
    
    def display_state(self, state: GameState):
        """Display current game state"""
        print("\n" + "="*60)
        print(f"STREET: {state.street.upper()}")
        print(f"POT: ${state.pot}")
        print(f"CURRENT BET: ${state.current_bet}")
        print("="*60)
        
        # Display community cards
        if state.community_cards:
            print(f"COMMUNITY CARDS: {' '.join(state.community_cards)}")
        else:
            print("COMMUNITY CARDS: (none)")
        
        print("\nPLAYERS:")
        print("-" * 60)
        
        for i, player in enumerate(state.players):
            status_indicator = "→" if i == state.current_player_index else " "
            status_str = f"[{player.status.value.upper()}]"
            
            hole_cards_str = ""
            if player.hole_cards:
                hole_cards_str = f" Cards: {' '.join(player.hole_cards)}"
            
            position_str = f"({player.position.value})" if player.position else ""
            
            print(f"{status_indicator} {player.id} {position_str} {status_str}")
            print(f"   Stack: ${player.stack} | Current Bet: ${player.current_bet}{hole_cards_str}")
        
        print("-" * 60)
    
    def display_message(self, message: str):
        """Display a message"""
        print(message)
    
    def get_player_action(self, state: GameState, legal_actions: List[str]) -> str:
        """Get action input from current player"""
        current_player = state.current_player
        print(f"\nAvailable actions: {', '.join(legal_actions)}")
        print("Commands: f=fold, c=call, ch=check, r <amount>=raise, a=all-in")
        
        while True:
            try:
                action = input(f"{current_player.id}, enter your action: ").strip()
                if action:
                    return action
                print("Please enter an action.")
            except KeyboardInterrupt:
                print("\nExiting game...")
                sys.exit(0)
            except EOFError:
                print("\nExiting game...")
                sys.exit(0)
    
    def run_game(self, config: GameConfig):
        """Run a complete poker game"""
        print(f"\nStarting {config.num_players}-player No-Limit Texas Hold'em")
        print(f"Blinds: ${config.small_blind}/${config.big_blind}")
        print(f"Starting stacks: ${config.starting_stack}")
        print("\nType 'help' during the game for command help, or Ctrl+C to quit.")
        
        try:
            # Start the game
            initial_state = self.game_loop.start_game(config)
            
            # Run the main game loop
            final_state = self.game_loop.run_game_loop(
                get_player_action=self.get_player_action,
                display_state=self.display_state,
                display_message=self.display_message
            )
            
            print("\nGame completed successfully!")
            
        except KeyboardInterrupt:
            print("\n\nGame interrupted by user.")
        except Exception as e:
            print(f"\nGame error: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Poker System MVP - No-Limit Texas Hold'em")
    parser.add_argument("--players", type=int, default=3, 
                       help="Number of players (2-9, default: 3)")
    parser.add_argument("--sb", "--small-blind", type=int, default=10,
                       help="Small blind amount (default: 10)")
    parser.add_argument("--bb", "--big-blind", type=int, default=20,
                       help="Big blind amount (default: 20)")
    parser.add_argument("--stack", "--starting-stack", type=int, default=1000,
                       help="Starting stack size (default: 1000)")
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.players < 2 or args.players > 9:
        print("Error: Number of players must be between 2 and 9")
        return 1
    
    if args.sb <= 0 or args.bb <= 0:
        print("Error: Blinds must be positive numbers")
        return 1
    
    if args.bb <= args.sb:
        print("Error: Big blind must be larger than small blind")
        return 1
    
    if args.stack <= args.bb * 2:
        print("Error: Starting stack must be at least 2x the big blind")
        return 1
    
    # Create game configuration
    config = GameConfig(
        num_players=args.players,
        small_blind=args.sb,
        big_blind=args.bb,
        starting_stack=args.stack
    )
    
    # Initialize and run the CLI
    cli = PokerCLI()
    cli.run_game(config)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())