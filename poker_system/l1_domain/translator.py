from abc import ABC, abstractmethod
from typing import Protocol, Any, List
from collections import namedtuple

from .game_state import GameState
from .action import Action


class Translator(Protocol):
    """Protocol defining the narrow interface between L1 (Domain) and L2 (Executor)"""
    
    def to_engine_state(self, game_state: GameState) -> Any:
        """Convert L1 GameState to engine-specific state (e.g., PokerKit State)"""
        ...
    
    def from_engine_state(self, engine_state: Any) -> GameState:
        """Convert engine-specific state back to L1 GameState"""
        ...
    
    def to_engine_action(self, action: Action, game_state: GameState) -> Any:
        """Convert L1 Action to engine-specific action"""
        ...
    
    def get_legal_actions(self, game_state: GameState) -> List[str]:
        """Get list of legal action strings for current player"""
        ...


StepResult = namedtuple('StepResult', ['game_state', 'events', 'is_terminal'])


class GameEngine(ABC):
    """Abstract interface for game engines"""
    
    @abstractmethod
    def create_initial_state(self, config: Any) -> GameState:
        """Create initial game state from configuration"""
        pass
    
    @abstractmethod
    def step(self, game_state: GameState, action: Action) -> StepResult:
        """Execute one action and return new state"""
        pass
    
    @abstractmethod
    def get_legal_actions(self, game_state: GameState) -> List[str]:
        """Get legal actions for current player"""
        pass


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