import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from l1_domain.game_state import GameConfig

# Try to import components
try:
    from l1_domain.rules import PokerRules
    L1_AVAILABLE = True
except ImportError:
    L1_AVAILABLE = False

try:
    from l2_executor.pokerkit_executor import PokerKitExecutor
    from l3_driver.game_loop import GameLoop
    FULL_STACK_AVAILABLE = True
except ImportError:
    FULL_STACK_AVAILABLE = False


class TestIntegration(unittest.TestCase):
    """End-to-end integration tests"""
    
    def setUp(self):
        if FULL_STACK_AVAILABLE:
            try:
                self.executor = PokerKitExecutor()
                self.game_loop = GameLoop(self.executor)
                self.has_full_stack = True
            except ImportError:
                self.has_full_stack = False
        else:
            self.has_full_stack = False
    
    @unittest.skipUnless(L1_AVAILABLE, "L1 rules not available")
    def test_l1_rules_independent_operation(self):
        """Test that L1 rules work independently"""
        # This test doesn't need PokerKit at all
        from l1_domain.game_state import GameState, Player, PlayerStatus
        
        players = (
            Player("P1", 1000, status=PlayerStatus.ACTIVE),
            Player("P2", 0, status=PlayerStatus.FOLDED),
        )
        state = GameState(
            players=players, community_cards=(), pot=100,
            current_player_index=0, dealer_index=0,
            small_blind=10, big_blind=20, current_bet=0,
            street="preflop", is_terminal=True
        )
        
        # L1 rules should work without any external dependencies
        winners, payouts = PokerRules.determine_winners(state)
        self.assertEqual(winners, [0])
        self.assertEqual(payouts[0], 100)
    
    @unittest.skipUnless(FULL_STACK_AVAILABLE, "Full stack not available")
    def test_game_initialization(self):
        """Test complete game initialization"""
        if not self.has_full_stack:
            self.skipTest("Full stack not available")
        
        config = GameConfig(2, 10, 20, 1000)
        initial_state = self.game_loop.start_game(config)
        
        # Verify initial state
        self.assertEqual(len(initial_state.players), 2)
        self.assertEqual(initial_state.small_blind, 10)
        self.assertEqual(initial_state.big_blind, 20)
        self.assertFalse(initial_state.is_terminal)
        self.assertIsNone(initial_state.winner_index)
        
        # Verify L1 rules can analyze this state (if available)
        if L1_AVAILABLE:
            is_complete = PokerRules.is_game_complete(initial_state)
            self.assertFalse(is_complete)  # Game just started
    
    @unittest.skipUnless(FULL_STACK_AVAILABLE and L1_AVAILABLE, "Full stack with L1 not available")
    def test_l1_l2_integration(self):
        """Test L1 and L2 integration after Track 1 completion"""
        if not self.has_full_stack:
            self.skipTest("Full stack not available")
        
        config = GameConfig(2, 10, 20, 1000)
        initial_state = self.game_loop.start_game(config)
        
        # Test that L2 can create state that L1 can process
        self.assertIsNotNone(initial_state)
        
        # Test L1 rules on L2-generated state
        is_complete = PokerRules.is_game_complete(initial_state)
        self.assertIsInstance(is_complete, bool)
        
        # TODO: Add more integration tests after all tracks merge


class TestArchitectureBoundaries(unittest.TestCase):
    """Test that architecture boundaries are maintained"""
    
    @unittest.skipUnless(L1_AVAILABLE, "L1 not available")
    def test_l1_has_no_external_dependencies(self):
        """Test that L1 domain has no external dependencies"""
        # L1 should be importable without any external libraries
        try:
            from l1_domain.rules import PokerRules
            from l1_domain.game_state import GameState, Player
            from l1_domain.action import Action, FoldAction
            
            # These imports should succeed regardless of PokerKit availability
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"L1 domain should not have external dependencies: {e}")


if __name__ == '__main__':
    unittest.main()