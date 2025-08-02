#!/usr/bin/env python3
"""
L5 CLI Layer: Pure argument parsing and delegation

This layer is responsible ONLY for:
1. Parsing command line arguments
2. Delegating to L3 driver
3. Providing help and version information

All game logic, UI logic, and business logic is handled by lower layers.
"""

import sys
import os
import argparse

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from l3_driver.cli_runner import run_cli


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser"""
    parser = argparse.ArgumentParser(
        description="Poker System MVP - No-Limit Texas Hold'em",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Default: 3 players, $10/$20, $1000 stacks
  %(prog)s --players 2 --sb 5 --bb 10 --stack 500
  %(prog)s --players 6 --sb 25 --bb 50 --stack 2000

For more information, visit: https://github.com/your-repo/poker-system-mvp
        """
    )
    
    parser.add_argument(
        "--players", 
        type=int, 
        default=3, 
        metavar="N",
        help="Number of players (2-9, default: %(default)s)"
    )
    
    parser.add_argument(
        "--sb", "--small-blind", 
        type=int, 
        default=10,
        metavar="AMOUNT", 
        help="Small blind amount (default: $%(default)s)"
    )
    
    parser.add_argument(
        "--bb", "--big-blind", 
        type=int, 
        default=20,
        metavar="AMOUNT",
        help="Big blind amount (default: $%(default)s)"
    )
    
    parser.add_argument(
        "--stack", "--starting-stack", 
        type=int, 
        default=1000,
        metavar="AMOUNT",
        help="Starting stack size (default: $%(default)s)"
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version="%(prog)s 1.0.0-MVP"
    )
    
    return parser


def main():
    """Pure argument parsing - delegate everything to L3"""
    try:
        parser = create_parser()
        args = parser.parse_args()
        
        # Convert to dict and delegate to L3
        config_dict = vars(args)
        run_cli(config_dict)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nExited by user.")
        return 130
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())