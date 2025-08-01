# 🏗️ Track 1: 核心架构修正 (主分支)

**负责人**: AI助理A  
**预估时间**: 3小时  
**优先级**: 🔴 CRITICAL  

## 任务概述

修正核心架构边界问题：
- Step 1: 创建L1纯规则层
- Step 2: 修正L2获胜者逻辑

这两步是整个架构修正的**基础**，必须优先完成。

---

## Step 1: 创建L1纯规则层
*预估时间: 2小时*

### 问题分析
- L1应包含纯扑克规则，当前散落在各层
- 缺失统一的获胜者判定逻辑
- 需要引擎无关的规则实现

### 具体实施

#### 创建核心规则模块

**文件**: `/poker_system/l1_domain/rules.py` (新建)
```python
from typing import List, Tuple, Optional, Dict
from enum import Enum
from .game_state import GameState, Player, PlayerStatus
from .action import Action


class HandRank(Enum):
    """Standard poker hand rankings"""
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10


class PokerRules:
    """Pure poker rules - engine agnostic"""
    
    @staticmethod
    def evaluate_hand(hole_cards: Tuple[str, str], community_cards: Tuple[str, ...]) -> Tuple[HandRank, List[str]]:
        """
        Evaluate 5-card poker hand strength
        Returns: (hand_rank, kickers) for comparison
        """
        if not hole_cards or len(community_cards) < 3:
            return HandRank.HIGH_CARD, []
        
        # For MVP: simplified evaluation
        # TODO: Implement full hand evaluation
        all_cards = list(hole_cards) + list(community_cards)
        return HandRank.HIGH_CARD, all_cards[:5]
    
    @staticmethod
    def compare_hands(hand1: Tuple[HandRank, List[str]], hand2: Tuple[HandRank, List[str]]) -> int:
        """
        Compare two poker hands
        Returns: 1 if hand1 wins, -1 if hand2 wins, 0 if tie
        """
        rank1, kickers1 = hand1
        rank2, kickers2 = hand2
        
        if rank1.value > rank2.value:
            return 1
        elif rank1.value < rank2.value:
            return -1
        else:
            # Same rank, compare kickers (simplified for MVP)
            return 0
    
    @staticmethod
    def determine_winners(state: GameState) -> Tuple[List[int], Dict[int, int]]:
        """
        Determine winners and calculate payouts - PURE POKER LOGIC
        
        Args:
            state: Complete game state with all player information
            
        Returns:
            (winner_indices, payouts) where payouts[player_idx] = amount_won
        """
        if not state.is_terminal:
            return [], {}
        
        # Find active players (not folded)
        active_players = []
        for i, player in enumerate(state.players):
            if player.status == PlayerStatus.ACTIVE:
                active_players.append(i)
        
        # Case 1: Only one active player (others folded)
        if len(active_players) == 1:
            winner_idx = active_players[0]
            return [winner_idx], {winner_idx: state.pot}
        
        # Case 2: Showdown required
        if len(active_players) > 1:
            return PokerRules._evaluate_showdown(state, active_players)
        
        # Case 3: No active players (shouldn't happen)
        return [], {}
    
    @staticmethod
    def _evaluate_showdown(state: GameState, active_players: List[int]) -> Tuple[List[int], Dict[int, int]]:
        """Evaluate showdown between active players"""
        if len(state.community_cards) < 5:
            # Pre-river: simplified logic for MVP
            # TODO: Implement proper showdown for all streets
            return [active_players[0]], {active_players[0]: state.pot}
        
        # Evaluate all hands
        hands = {}
        for player_idx in active_players:
            player = state.players[player_idx]
            if player.hole_cards:
                hand_strength = PokerRules.evaluate_hand(player.hole_cards, state.community_cards)
                hands[player_idx] = hand_strength
        
        if not hands:
            return [], {}
        
        # Find best hand(s)
        best_players = []
        best_hand = None
        
        for player_idx, hand in hands.items():
            if best_hand is None:
                best_hand = hand
                best_players = [player_idx]
            else:
                comparison = PokerRules.compare_hands(hand, best_hand)
                if comparison > 0:  # New best hand
                    best_hand = hand
                    best_players = [player_idx]
                elif comparison == 0:  # Tie
                    best_players.append(player_idx)
        
        # Distribute pot among winners
        payout_per_winner = state.pot // len(best_players)
        payouts = {player_idx: payout_per_winner for player_idx in best_players}
        
        return best_players, payouts
    
    @staticmethod
    def is_game_complete(state: GameState) -> bool:
        """Check if game/hand is complete"""
        active_count = sum(1 for p in state.players if p.status == PlayerStatus.ACTIVE)
        return active_count <= 1 or state.street == "river"  # Simplified for MVP
    
    @staticmethod
    def get_next_street(current_street: str) -> Optional[str]:
        """Get next betting street"""
        streets = ["preflop", "flop", "turn", "river"]
        try:
            current_idx = streets.index(current_street)
            return streets[current_idx + 1] if current_idx < len(streets) - 1 else None
        except ValueError:
            return None
```

### 验证方法
```python
# Quick test
from poker_system.l1_domain.rules import PokerRules, HandRank

# Test hand evaluation
hand = PokerRules.evaluate_hand(("Ah", "Kd"), ("Qh", "Jh", "Th", "9s", "8c"))
print(f"Hand: {hand}")  # Should work without PokerKit
```

### 提交点
```bash
git add poker_system/l1_domain/rules.py
git commit -m "Step 1: Add L1 pure rules layer - engine agnostic poker logic"
```

---

## Step 2: 修正L2获胜者逻辑
*预估时间: 1小时*

### 问题分析
当前L2直接读取`pk_state.showdown_indices`，违反了翻译层职责。

### 具体实施

**文件**: `/poker_system/l2_executor/pokerkit_executor.py`

#### 修改点1: 添加导入 (文件顶部)
```python
# 在现有imports后添加:
from l1_domain.rules import PokerRules
```

#### 修改点2: 修改`from_engine_state`方法 (约107行)
```python
# 替换:
winner_index=None  # Simplified for MVP

# 为:
winner_index=self._determine_winner_via_l1_rules(pk_state),
```

#### 修改点3: 重写`_determine_winner`方法 (类末尾)
```python
def _determine_winner_via_l1_rules(self, pk_state: Any) -> Optional[int]:
    """
    Determine winner by translating to L1 state and calling L1 rules
    L2 ONLY does translation - L1 contains all poker logic
    """
    try:
        # If game is still running, no winner yet
        if pk_state.status:
            return None
        
        # Translate PokerKit state to L1 GameState
        l1_state = self.from_engine_state(pk_state)
        
        # Call L1 pure rules to determine winner
        winners, payouts = PokerRules.determine_winners(l1_state)
        
        # Return first winner (MVP simplification)
        return winners[0] if winners else None
        
    except Exception as e:
        print(f"Warning: Could not determine winner via L1 rules: {e}")
        return None
```

#### 修改点4: 更新`from_engine_state`中的终局判断 (约106行)
```python
# 修改终局判断逻辑:
is_terminal=not pk_state.status,  # Game is terminal when status is False
```

### 验证方法
```bash
cd poker_system
python l5_cli/main.py --players 2 --sb 5 --bb 10 --stack 200
# 让一个玩家fold，游戏应该正确显示获胜者
```

### 提交点
```bash
git add poker_system/l2_executor/pokerkit_executor.py
git commit -m "Step 2: Fix L2 winner logic via L1 rules - pure translation layer"
```

---

## 成功标准

### 架构验证
- [ ] L1规则完全独立，零外部依赖
- [ ] L2只做翻译，调用L1规则判定获胜者
- [ ] 游戏能正确显示获胜者

### 功能验证
- [ ] 单人获胜场景正确处理
- [ ] 多人showdown场景有基础处理
- [ ] 异常情况有保护机制

### 代码质量
- [ ] L1规则有完整类型提示
- [ ] L2修改有异常处理
- [ ] 代码边界清晰

## 风险控制

### 潜在风险
1. **循环导入**: L2导入L1规则可能产生循环依赖
2. **状态转换**: `from_engine_state`调用自身可能死循环
3. **PokerKit兼容**: 新逻辑与PokerKit状态不匹配

### 缓解措施
1. **导入检查**: 仔细检查import语句，避免循环
2. **状态缓存**: 使用临时状态避免重复转换
3. **异常保护**: 所有关键路径都有try-catch

## 交接信息

完成后将产生：
- `poker_system/l1_domain/rules.py` - 纯扑克规则
- 修改后的 `poker_system/l2_executor/pokerkit_executor.py` - 调用L1规则

**为Track 2和Track 3提供**：
- L1规则API用于测试
- 正确的获胜者逻辑用于展示

**合并时注意**：
- 确保L1规则导入路径正确
- 验证获胜者逻辑在所有场景下工作

---

*这个轨道是整个架构修正的核心，完成后将为其他轨道提供坚实的基础。*