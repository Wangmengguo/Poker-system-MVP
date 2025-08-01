import unittest
import sys
import os

# Add parent directory for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from l1_domain.game_state import GameConfig
from l1_domain.translator import MockTranslator

# Try to import L2 components
try:
    from l2_executor.pokerkit_executor import PokerKitExecutor
    POKERKIT_AVAILABLE = True
except ImportError:
    POKERKIT_AVAILABLE = False


class TestL2Translator(unittest.TestCase):
    """Test L2 translation layer integration with L1"""
    
    def setUp(self):
        """Set up test fixtures"""
        if POKERKIT_AVAILABLE:
            try:
                self.executor = PokerKitExecutor()
                self.has_pokerkit = True
            except ImportError:
                self.has_pokerkit = False
        else:
            self.has_pokerkit = False
    
    def test_mock_translator_protocol_compliance(self):
        """Test that MockTranslator implements Protocol correctly"""
        mock = MockTranslator()
        
        # All methods should raise NotImplementedError
        with self.assertRaises(NotImplementedError):
            mock.to_engine_state(None)
        
        with self.assertRaises(NotImplementedError):
            mock.from_engine_state(None)
        
        with self.assertRaises(NotImplementedError):
            mock.to_engine_action(None, None)
        
        with self.assertRaises(NotImplementedError):
            mock.get_legal_actions(None)
    
    @unittest.skipUnless(POKERKIT_AVAILABLE, "PokerKit not available")
    def test_l2_initialization(self):
        """Test that L2 executor can be initialized"""
        if not self.has_pokerkit:
            self.skipTest("PokerKit not available")
        
        # Should not raise exception
        executor = PokerKitExecutor()
        self.assertIsNotNone(executor)
    
    @unittest.skipUnless(POKERKIT_AVAILABLE, "PokerKit not available")
    def test_l2_game_creation(self):
        """Test that L2 can create initial game state"""
        if not self.has_pokerkit:
            self.skipTest("PokerKit not available")
        
        config = GameConfig(2, 10, 20, 1000)
        initial_state = self.executor.create_initial_state(config)
        
        # Verify basic state properties
        self.assertEqual(len(initial_state.players), 2)
        self.assertEqual(initial_state.small_blind, 10)
        self.assertEqual(initial_state.big_blind, 20)
        self.assertFalse(initial_state.is_terminal)
        
        # After Track 1 completion, winner should be None initially
        # Note: This test will be enhanced after Track 1 merge
        
    @unittest.skipUnless(POKERKIT_AVAILABLE, "PokerKit not available")  
    def test_l2_calls_l1_rules_for_winner(self):
        """Test that L2 properly delegates winner determination to L1"""
        if not self.has_pokerkit:
            self.skipTest("PokerKit not available")
        
        config = GameConfig(2, 10, 20, 1000)
        initial_state = self.executor.create_initial_state(config)
        
        # Initial state should not have a winner
        self.assertIsNone(initial_state.winner_index)
        
        # TODO: Add more comprehensive integration tests after Track 1 merge
        # This will test that L2 actually calls L1 rules for winner determination


class TestProtocolCompliance(unittest.TestCase):
    """Test Protocol compliance without external dependencies"""
    
    def test_mock_translator_interface(self):
        """Test MockTranslator implements required interface"""
        mock = MockTranslator()
        
        # Check that all required methods exist
        self.assertTrue(hasattr(mock, 'to_engine_state'))
        self.assertTrue(hasattr(mock, 'from_engine_state'))
        self.assertTrue(hasattr(mock, 'to_engine_action'))
        self.assertTrue(hasattr(mock, 'get_legal_actions'))
        
        # Check that methods are callable
        self.assertTrue(callable(mock.to_engine_state))
        self.assertTrue(callable(mock.from_engine_state))
        self.assertTrue(callable(mock.to_engine_action))
        self.assertTrue(callable(mock.get_legal_actions))


if __name__ == '__main__':
    unittest.main()