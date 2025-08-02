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