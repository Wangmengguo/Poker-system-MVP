from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ActionType(Enum):
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    RAISE = "raise"
    ALL_IN = "all_in"


@dataclass(frozen=True)
class Action(ABC):
    action_type: ActionType
    player_id: str
    
    @abstractmethod
    def is_valid(self, current_bet: int, player_stack: int, player_current_bet: int) -> bool:
        pass


@dataclass(frozen=True)
class FoldAction(Action):
    def __init__(self, player_id: str):
        super().__init__(ActionType.FOLD, player_id)
    
    def is_valid(self, current_bet: int, player_stack: int, player_current_bet: int) -> bool:
        return True


@dataclass(frozen=True)
class CheckAction(Action):
    def __init__(self, player_id: str):
        super().__init__(ActionType.CHECK, player_id)
    
    def is_valid(self, current_bet: int, player_stack: int, player_current_bet: int) -> bool:
        return current_bet == player_current_bet


@dataclass(frozen=True)
class CallAction(Action):
    def __init__(self, player_id: str):
        super().__init__(ActionType.CALL, player_id)
    
    def is_valid(self, current_bet: int, player_stack: int, player_current_bet: int) -> bool:
        call_amount = current_bet - player_current_bet
        return call_amount > 0 and call_amount <= player_stack


@dataclass(frozen=True)
class RaiseAction(Action):
    amount: int
    
    def __init__(self, player_id: str, amount: int):
        super().__init__(ActionType.RAISE, player_id)
        object.__setattr__(self, 'amount', amount)
    
    def is_valid(self, current_bet: int, player_stack: int, player_current_bet: int) -> bool:
        total_bet = player_current_bet + self.amount
        return (total_bet > current_bet and 
                self.amount <= player_stack and
                self.amount > 0)


@dataclass(frozen=True)
class AllInAction(Action):
    def __init__(self, player_id: str):
        super().__init__(ActionType.ALL_IN, player_id)
    
    def is_valid(self, current_bet: int, player_stack: int, player_current_bet: int) -> bool:
        return player_stack > 0


def parse_action(action_str: str, player_id: str) -> Optional[Action]:
    action_str = action_str.strip().lower()
    
    if action_str == "f" or action_str == "fold":
        return FoldAction(player_id)
    elif action_str == "c" or action_str == "call":
        return CallAction(player_id)
    elif action_str == "ch" or action_str == "check":
        return CheckAction(player_id)
    elif action_str.startswith("r ") or action_str.startswith("raise "):
        try:
            parts = action_str.split()
            if len(parts) >= 2:
                amount = int(parts[1])
                return RaiseAction(player_id, amount)
        except ValueError:
            pass
    elif action_str == "a" or action_str == "all-in" or action_str == "allin":
        return AllInAction(player_id)
    
    return None