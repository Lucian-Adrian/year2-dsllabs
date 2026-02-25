"""
Abstract base classes for Grammar and Automaton.
Following OCP - these base classes are open for extension, closed for modification.
"""

from abc import ABC, abstractmethod
from typing import Set, Dict, List, Any


class Grammar(ABC):
    """
    Abstract base class for all Grammars.

    Open for extension: Add new grammar types by inheriting from this class.
    Closed for modification: No need to modify this class to add new grammar types.
    """

    @abstractmethod
    def __init__(self, vn: Set[str], vt: Set[str], productions: Dict[str, List[str]]):
        """Initialize grammar with non-terminals, terminals, and productions."""
        self.vn: Set[str] = vn
        self.vt: Set[str] = vt
        self.productions: Dict[str, List[str]] = productions

    @abstractmethod
    def get_chomsky_type(self) -> int:
        """Return the Chomsky hierarchy type (0-3)."""
        pass

    @abstractmethod
    def generate_word(self) -> str:
        """Generate a random word from the grammar."""
        pass


class Automaton(ABC):
    """
    Abstract base class for all Automata.

    Open for extension: Add new automaton types by inheriting from this class.
    Closed for modification: No need to modify this class to add new automaton types.
    """

    @abstractmethod
    def __init__(
        self,
        states: Set[str],
        alphabet: Set[str],
        transitions: List[tuple],
        start_state: str,
        final_states: Set[str],
    ):
        """
        Initialize automaton with states, alphabet, transitions, start, and final states.

        Transitions format: [(state, symbol, next_state), ...]
        """
        self.states: Set[str] = states
        self.alphabet: Set[str] = alphabet
        self.transitions: List[tuple] = transitions
        self.start_state: str = start_state
        self.final_states: Set[str] = final_states

    @abstractmethod
    def accepts(self, word: str) -> bool:
        """Check if the automaton accepts a given word."""
        pass

    @abstractmethod
    def get_type(self) -> str:
        """Return 'DFA' or 'NFA'."""
        pass
