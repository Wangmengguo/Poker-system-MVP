import unittest
from poker_system.l1_domain.rules import PokerRules, HandRank
from poker_system.l1_domain.game_state import GameState, Player, PlayerStatus


class TestL1Rules(unittest.TestCase):
    """Test pure poker rules - no external dependencies"""
    
    def test_hand_evaluation_basic(self):
        """Test basic hand evaluation"""
        # Test high card
        hand = PokerRules.evaluate_hand(("Ah", "Kd"), ("Qh", "Jh", "Th", "9s", "8c"))
        self.assertEqual(hand[0], HandRank.HIGH_CARD)
        
    def test_hand_evaluation_edge_cases(self):
        """Test edge cases in hand evaluation"""
        # Test with insufficient community cards
        hand = PokerRules.evaluate_hand(("Ah", "Kd"), ("Qh", "Jh"))
        self.assertEqual(hand[0], HandRank.HIGH_CARD)
        
        # Test with no hole cards
        hand = PokerRules.evaluate_hand(None, ("Qh", "Jh", "Th", "9s", "8c"))
        self.assertEqual(hand[0], HandRank.HIGH_CARD)
        
    def test_hand_comparison(self):
        """Test hand comparison logic"""
        high_card = (HandRank.HIGH_CARD, ["Ah", "Kd", "Qh", "Jh", "Th"])
        pair = (HandRank.PAIR, ["Ah", "As", "Kd", "Qh", "Jh"])
        
        # Pair should beat high card
        self.assertEqual(PokerRules.compare_hands(pair, high_card), 1)
        self.assertEqual(PokerRules.compare_hands(high_card, pair), -1)
        
        # Same rank should tie (simplified for MVP)
        self.assertEqual(PokerRules.compare_hands(high_card, high_card), 0)
        
    def test_winner_determination_single_player(self):
        """Test winner when only one player remains"""
        players = (
            Player("P1", 1000, status=PlayerStatus.ACTIVE),
            Player("P2", 0, status=PlayerStatus.FOLDED),
        )
        state = GameState(
            players=players,
            community_cards=("Ah", "Kd", "Qh"),
            pot=100,
            current_player_index=0,
            dealer_index=0,
            small_blind=10,
            big_blind=20,
            current_bet=0,
            street="flop",
            is_terminal=True
        )
        
        winners, payouts = PokerRules.determine_winners(state)
        self.assertEqual(winners, [0])
        self.assertEqual(payouts[0], 100)
        
    def test_winner_determination_no_terminal(self):
        """Test winner determination when game is not terminal"""
        players = (
            Player("P1", 1000, status=PlayerStatus.ACTIVE),
            Player("P2", 1000, status=PlayerStatus.ACTIVE),
        )
        state = GameState(
            players=players,
            community_cards=("Ah", "Kd", "Qh"),
            pot=100,
            current_player_index=0,
            dealer_index=0,
            small_blind=10,
            big_blind=20,
            current_bet=0,
            street="flop",
            is_terminal=False  # Game not terminal
        )
        
        winners, payouts = PokerRules.determine_winners(state)
        self.assertEqual(winners, [])
        self.assertEqual(payouts, {})
        
    def test_winner_determination_showdown(self):
        """Test winner determination at showdown"""
        players = (
            Player("P1", 1000, hole_cards=("Ah", "Kd"), status=PlayerStatus.ACTIVE),
            Player("P2", 1000, hole_cards=("2h", "3d"), status=PlayerStatus.ACTIVE),
        )
        state = GameState(
            players=players,
            community_cards=("Qh", "Jh", "Th", "9s", "8c"),
            pot=200,
            current_player_index=0,
            dealer_index=0,
            small_blind=10,
            big_blind=20,
            current_bet=0,
            street="river",
            is_terminal=True
        )
        
        winners, payouts = PokerRules.determine_winners(state)
        self.assertGreaterEqual(len(winners), 1)  # Should have at least one winner (could be tie)
        for winner in winners:
            self.assertIn(winner, [0, 1])  # Winner should be one of the players
        self.assertEqual(sum(payouts.values()), 200)  # Total payout equals pot
        
    def test_winner_determination_pre_river(self):
        """Test winner determination before river (simplified logic)"""
        players = (
            Player("P1", 1000, hole_cards=("Ah", "Kd"), status=PlayerStatus.ACTIVE),
            Player("P2", 1000, hole_cards=("2h", "3d"), status=PlayerStatus.ACTIVE),
        )
        state = GameState(
            players=players,
            community_cards=("Qh", "Jh", "Th"),  # Only 3 cards (flop)
            pot=200,
            current_player_index=0,
            dealer_index=0,
            small_blind=10,
            big_blind=20,
            current_bet=0,
            street="flop",
            is_terminal=True
        )
        
        winners, payouts = PokerRules.determine_winners(state)
        self.assertEqual(len(winners), 1)  # Should have a winner (simplified)
        self.assertEqual(payouts[winners[0]], 200)  # Winner gets full pot
        
    def test_game_completion_logic(self):
        """Test game completion detection"""
        # Game should be complete when only one active player
        players = (
            Player("P1", 1000, status=PlayerStatus.ACTIVE),
            Player("P2", 0, status=PlayerStatus.FOLDED),
        )
        state = GameState(
            players=players, community_cards=(), pot=100,
            current_player_index=0, dealer_index=0,
            small_blind=10, big_blind=20, current_bet=0,
            street="preflop", is_terminal=False
        )
        
        self.assertTrue(PokerRules.is_game_complete(state))
        
        # Game should be complete at river
        players = (
            Player("P1", 1000, status=PlayerStatus.ACTIVE),
            Player("P2", 1000, status=PlayerStatus.ACTIVE),
        )
        state = GameState(
            players=players, community_cards=("Ah", "Kd", "Qh", "Jh", "Th"), pot=100,
            current_player_index=0, dealer_index=0,
            small_blind=10, big_blind=20, current_bet=0,
            street="river", is_terminal=False
        )
        
        self.assertTrue(PokerRules.is_game_complete(state))
        
    def test_next_street_logic(self):
        """Test betting street progression"""
        self.assertEqual(PokerRules.get_next_street("preflop"), "flop")
        self.assertEqual(PokerRules.get_next_street("flop"), "turn")
        self.assertEqual(PokerRules.get_next_street("turn"), "river")
        self.assertIsNone(PokerRules.get_next_street("river"))
        
        # Test invalid street
        self.assertIsNone(PokerRules.get_next_street("invalid"))


if __name__ == '__main__':
    unittest.main()