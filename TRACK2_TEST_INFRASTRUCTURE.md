# 🧪 Track 2: 测试基础设施 (tests-track)

**负责人**: AI助理B  
**预估时间**: 1.5小时  
**优先级**: 🟡 HIGH  

## 任务概述

建立正确的测试基础设施：
- Step 3: 修正测试策略，创建完整测试套件
- 修正MockTranslator实现
- 确保L1规则可独立测试

这个轨道可以与Track 1并行开发，为质量保证提供基础。

---

## Step 3: 修正测试基础设施
*预估时间: 1.5小时*

### 问题分析
- 当前缺乏测试基础设施
- Mock实现返回假数据，掩盖真实问题
- L1规则需要独立测试能力

### 具体实施

#### 修正Mock实现

**文件**: `/poker_system/l1_domain/translator.py` (文件末尾添加)
```python

class MockTranslator:
    """
    Skeleton mock for Protocol compliance testing
    DOES NOT return fake data - only validates Protocol interface
    """
    
    def to_engine_state(self, game_state: GameState) -> Any:
        raise NotImplementedError("Mock implementation - use real translator for actual testing")
    
    def from_engine_state(self, engine_state: Any) -> GameState:
        raise NotImplementedError("Mock implementation - use real translator for actual testing")
    
    def to_engine_action(self, action: Action, game_state: GameState) -> Any:
        raise NotImplementedError("Mock implementation - use real translator for actual testing")
    
    def get_legal_actions(self, game_state: GameState) -> List[str]:
        raise NotImplementedError("Mock implementation - use real translator for actual testing")
```

#### 创建测试包

**文件**: `/poker_system/tests/__init__.py` (新建)
```python
# Tests package for Poker System MVP
"""
Test suite for Poker System MVP

This package contains tests for all layers:
- test_l1_rules.py: Pure domain logic tests (no external dependencies)
- test_l2_translator.py: Translation layer integration tests  
- test_integration.py: End-to-end integration tests

Design philosophy:
- L1 tests are completely independent
- L2 tests verify translator behavior
- Integration tests verify full system behavior
"""
```

#### 创建L1规则测试

**文件**: `/poker_system/tests/test_l1_rules.py` (新建)
```python
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
        self.assertEqual(len(winners), 1)  # Should have a winner
        self.assertIn(winners[0], [0, 1])  # Winner should be one of the players
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
```

#### 创建L2翻译测试

**文件**: `/poker_system/tests/test_l2_translator.py` (新建)
```python
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
```

#### 创建集成测试框架

**文件**: `/poker_system/tests/test_integration.py` (新建)
```python
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
```

### 验证方法
```bash
cd poker_system

# Test L1 rules independently (should work without PokerKit)
python -m pytest tests/test_l1_rules.py -v

# Test protocol compliance
python -m pytest tests/test_l2_translator.py::TestProtocolCompliance -v

# Test architecture boundaries  
python -m pytest tests/test_integration.py::TestArchitectureBoundaries -v

# Full test suite (may skip tests if dependencies missing)
python -m pytest tests/ -v
```

### 提交点
```bash
git add poker_system/l1_domain/translator.py
git add poker_system/tests/
git commit -m "Step 3: Add correct test infrastructure with proper Mock implementation"
```

---

## 成功标准

### 测试覆盖
- [ ] L1规则完全独立测试（无需PokerKit）
- [ ] MockTranslator正确实现Protocol骨架
- [ ] 集成测试框架就绪

### 质量保证
- [ ] 所有L1测试通过
- [ ] Mock测试验证Protocol合规性
- [ ] 架构边界测试通过

### 代码质量
- [ ] 测试有清晰的文档字符串
- [ ] 边界情况有覆盖
- [ ] 依赖缺失时优雅跳过

## 风险控制

### 潜在风险
1. **导入路径**: 测试文件的import路径可能不正确
2. **依赖缺失**: PokerKit缺失时测试应该优雅跳过
3. **Mock语义**: Mock实现可能与Protocol不匹配

### 缓解措施
1. **相对导入**: 使用sys.path.append确保导入正确
2. **条件跳过**: 使用@unittest.skipUnless处理依赖
3. **Protocol验证**: 专门测试Mock的Protocol合规性

## 交接信息

完成后将产生：
- 修改后的 `poker_system/l1_domain/translator.py` - 正确的Mock实现
- `poker_system/tests/` - 完整测试套件

**为其他轨道提供**：
- L1规则的独立测试验证
- Mock实现用于Protocol测试
- 集成测试框架

**合并时注意**：
- MockTranslator只在translator.py末尾添加
- 测试可能会因Track 1未完成而部分跳过
- 测试文件的import路径需要验证

---

*这个轨道建立了正确的测试基础，确保L1规则可以独立验证，为整个项目的质量提供保障。*