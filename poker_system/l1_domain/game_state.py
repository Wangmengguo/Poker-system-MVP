from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple
from collections import namedtuple


class Position(Enum):
    SMALL_BLIND = "SB"
    BIG_BLIND = "BB"
    UNDER_THE_GUN = "UTG"
    MIDDLE_POSITION = "MP"
    CUTOFF = "CO"
    BUTTON = "BTN"


class PlayerStatus(Enum):
    ACTIVE = "active"
    FOLDED = "folded"
    ALL_IN = "all_in"
    OUT = "out"


@dataclass(frozen=True)
class Player:
    id: str
    stack: int
    hole_cards: Optional[Tuple[str, str]] = None
    position: Optional[Position] = None
    status: PlayerStatus = PlayerStatus.ACTIVE
    current_bet: int = 0
    total_bet_this_hand: int = 0


@dataclass(frozen=True)
class GameState:
    players: Tuple[Player, ...]
    community_cards: Tuple[str, ...]
    pot: int
    current_player_index: int
    dealer_index: int
    small_blind: int
    big_blind: int
    current_bet: int
    street: str  # "preflop", "flop", "turn", "river"
    is_terminal: bool = False
    winner_index: Optional[int] = None
    
    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_index]
    
    @property
    def active_players(self) -> List[Player]:
        return [p for p in self.players if p.status == PlayerStatus.ACTIVE]
    
    def with_player_action(self, player_index: int, new_stack: int, new_bet: int, 
                          new_status: PlayerStatus = PlayerStatus.ACTIVE) -> 'GameState':
        new_players = list(self.players)
        old_player = new_players[player_index]
        new_players[player_index] = Player(
            id=old_player.id,
            stack=new_stack,
            hole_cards=old_player.hole_cards,
            position=old_player.position,
            status=new_status,
            current_bet=new_bet,
            total_bet_this_hand=old_player.total_bet_this_hand + (new_bet - old_player.current_bet)
        )
        
        return GameState(
            players=tuple(new_players),
            community_cards=self.community_cards,
            pot=self.pot + (new_bet - old_player.current_bet),
            current_player_index=self.current_player_index,
            dealer_index=self.dealer_index,
            small_blind=self.small_blind,
            big_blind=self.big_blind,
            current_bet=max(self.current_bet, new_bet),
            street=self.street,
            is_terminal=self.is_terminal,
            winner_index=self.winner_index
        )


GameConfig = namedtuple('GameConfig', ['num_players', 'small_blind', 'big_blind', 'starting_stack'])