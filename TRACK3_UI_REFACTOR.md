# 🎨 Track 3: UI重构和工具功能 (ui-track)

**负责人**: AI助理C  
**预估时间**: 2小时  
**优先级**: 🟡 MEDIUM  

## 任务概述

重构用户界面和添加工具功能：
- Step 4: CLI职责分离
- Step 5: 添加手牌历史和统计功能

这个轨道可以与Track 1并行开发，专注于用户体验和扩展功能。

---

## Step 4: CLI职责分离
*预估时间: 1小时*

### 问题分析
- 当前L5层包含过多业务逻辑
- CLI逻辑应该下沉到L3层
- L5应该只负责参数解析

### 具体实施

#### 创建CLI运行器

**文件**: `/poker_system/l3_driver/cli_runner.py` (新建)
```python
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
```

#### 简化L5层

**文件**: `/poker_system/l5_cli/main.py` (完全重写)
```python
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
```

### 验证方法
```bash
cd poker_system

# Test new CLI with better help
python l5_cli/main.py --help

# Test with validation errors
python l5_cli/main.py --players 1  # Should show error
python l5_cli/main.py --sb 20 --bb 10  # Should show error

# Test normal game (should work after Track 1 merge)
python l5_cli/main.py --players 2 --sb 5 --bb 10 --stack 200
```

### 提交点
```bash
git add poker_system/l3_driver/cli_runner.py
git add poker_system/l5_cli/main.py
git commit -m "Step 4: Separate CLI responsibilities - L5 pure parsing, L3 game logic"
```

---

## Step 5: 添加手牌历史和统计
*预估时间: 1小时*

### 问题分析
- 缺乏游戏数据导出功能
- 没有统计信息展示
- 需要为未来分析功能奠定基础

### 具体实施

#### 扩展GameLoop功能

**文件**: `/poker_system/l3_driver/game_loop.py` (在类末尾添加方法)
```python
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
```

#### 增强CLI运行器以支持导出

**文件**: `/poker_system/l3_driver/cli_runner.py` (修改run_single_game方法)

在现有的`run_single_game`方法中，在游戏结束后添加：

```python
# 在 "Game completed successfully!" 之前添加：

# Display enhanced game summary
self.game_loop.display_game_summary()

# Prompt for export
if final_state and final_state.is_terminal:
    self.game_loop.prompt_for_export()

print("\nGame completed successfully!")
```

#### 创建统计分析工具

**文件**: `/poker_system/l3_driver/analytics.py` (新建)
```python
"""
Analytics tools for poker game data analysis
"""

import json
from typing import Dict, List, Any
from datetime import datetime


class HandHistoryAnalyzer:
    """Analyze exported hand history data"""
    
    def __init__(self, history_file: str):
        self.history_file = history_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """Load hand history data from JSON file"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to load history file {self.history_file}: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the game"""
        summary = {
            "timestamp": self.data.get("timestamp"),
            "game_type": self.data.get("game_type"),
            "total_actions": len(self.data.get("hand_history", [])),
            "winner": None,
            "pot_size": 0
        }
        
        if "winner_analysis" in self.data and self.data["winner_analysis"]:
            summary["winner"] = self.data["winner_analysis"]["winner_id"]
            summary["pot_size"] = self.data["winner_analysis"]["pot_won"]
        
        if "final_state" in self.data and self.data["final_state"]:
            summary["final_street"] = self.data["final_state"]["street"]
            summary["num_players"] = len(self.data["final_state"]["players"])
        
        return summary
    
    def analyze_player_performance(self) -> Dict[str, Dict[str, Any]]:
        """Analyze individual player performance"""
        if "statistics" not in self.data or "players" not in self.data["statistics"]:
            return {}
        
        return self.data["statistics"]["players"]
    
    def get_action_timeline(self) -> List[str]:
        """Get chronological action timeline"""
        return self.data.get("hand_history", [])
    
    def export_summary_report(self, output_file: str = None) -> str:
        """Export a human-readable summary report"""
        summary = self.get_summary()
        players = self.analyze_player_performance()
        timeline = self.get_action_timeline()
        
        report_lines = [
            "POKER GAME ANALYSIS REPORT",
            "=" * 50,
            f"Game Type: {summary.get('game_type', 'Unknown')}",
            f"Timestamp: {summary.get('timestamp', 'Unknown')}",
            f"Players: {summary.get('num_players', 'Unknown')}",
            f"Final Street: {summary.get('final_street', 'Unknown').title()}",
            f"Total Actions: {summary.get('total_actions', 0)}",
            "",
            "RESULTS:",
            "-" * 20
        ]
        
        if summary.get("winner"):
            report_lines.extend([
                f"🏆 Winner: {summary['winner']}",
                f"💰 Pot Size: ${summary.get('pot_size', 0)}",
                ""
            ])
        
        if players:
            report_lines.append("PLAYER PERFORMANCE:")
            report_lines.append("-" * 20)
            for player_id, stats in players.items():
                status_icon = "🏆" if stats.get("is_winner") else "📊"
                report_lines.append(f"{status_icon} {player_id}:")
                report_lines.append(f"  Final Stack: ${stats.get('final_stack', 0)}")
                report_lines.append(f"  Position: {stats.get('position', 'Unknown')}")
                report_lines.append(f"  Status: {stats.get('status', 'Unknown').title()}")
                if stats.get("winnings", 0) > 0:
                    report_lines.append(f"  Winnings: ${stats['winnings']}")
                report_lines.append("")
        
        if timeline:
            report_lines.extend([
                "ACTION TIMELINE:",
                "-" * 20
            ])
            for i, action in enumerate(timeline, 1):
                report_lines.append(f"{i:2d}. {action}")
        
        report_text = "\n".join(report_lines)
        
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report_text)
                return f"Analysis report exported to {output_file}"
            except IOError as e:
                return f"Failed to export report: {e}"
        
        return report_text


# Command-line interface for analytics
def main():
    """Command-line interface for hand history analysis"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze poker hand history")
    parser.add_argument("history_file", help="JSON hand history file to analyze")
    parser.add_argument("--output", "-o", help="Output file for analysis report")
    parser.add_argument("--summary", "-s", action="store_true", help="Show summary only")
    
    args = parser.parse_args()
    
    try:
        analyzer = HandHistoryAnalyzer(args.history_file)
        
        if args.summary:
            summary = analyzer.get_summary()
            print(json.dumps(summary, indent=2))
        else:
            report = analyzer.export_summary_report(args.output)
            if args.output:
                print(report)
            else:
                print(report)
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### 验证方法
```bash
cd poker_system

# Test game with export functionality
python l5_cli/main.py --players 2

# After game ends, choose 'y' for export, then analyze the generated file
python l3_driver/analytics.py hand_history_*.json

# Test analytics with output
python l3_driver/analytics.py hand_history_*.json --output analysis_report.txt
```

### 提交点
```bash
git add poker_system/l3_driver/game_loop.py
git add poker_system/l3_driver/cli_runner.py  
git add poker_system/l3_driver/analytics.py
git commit -m "Step 5: Add hand history export and statistics analysis tools"
```

---

## 成功标准

### UI改进
- [ ] L5层职责纯化（仅参数解析）
- [ ] L3层承担所有CLI逻辑
- [ ] 用户体验改善（更好的错误提示、格式化）

### 功能扩展
- [ ] 手牌历史导出功能完整
- [ ] 统计信息详细准确
- [ ] 分析工具可用

### 代码质量
- [ ] 职责分离清晰
- [ ] 错误处理健壮
- [ ] 用户友好的提示信息

## 风险控制

### 潜在风险
1. **文件冲突**: main.py和game_loop.py的修改可能冲突
2. **功能依赖**: 统计功能可能依赖Track 1的获胜者逻辑
3. **用户体验**: CLI改动可能影响现有用户习惯

### 缓解措施
1. **小心合并**: 文件修改时保持向后兼容
2. **优雅降级**: 统计功能在获胜者逻辑缺失时也能部分工作
3. **保持兼容**: CLI参数和基本功能保持不变

## 交接信息

完成后将产生：
- `poker_system/l3_driver/cli_runner.py` - 新的CLI运行器
- 重写的 `poker_system/l5_cli/main.py` - 纯参数解析
- 扩展的 `poker_system/l3_driver/game_loop.py` - 导出和统计功能
- `poker_system/l3_driver/analytics.py` - 分析工具

**为其他轨道提供**：
- 改善的用户界面
- 数据导出和分析能力
- 清晰的层级职责分离

**合并时注意**：
- main.py被完全重写，确保功能等价
- game_loop.py只在末尾添加方法
- 新增的analytics.py是独立工具

**功能增强点**：
- 更好的错误提示和用户引导
- 游戏结束后的详细统计展示
- 手牌历史的完整导出
- 独立的分析工具

---

*这个轨道专注于用户体验和扩展功能，为项目提供了完整的数据分析能力和清晰的架构分层。*