"""
Regular Grammar implementation.
Single Responsibility: Only handles grammar-specific operations.
"""

import random
from typing import Set, Dict, List
from .base import Grammar


class RegularGrammar(Grammar):
    """
    Regular Grammar implementation.

    A regular grammar is a context-free grammar where all productions
    have the form: A -> aB or A -> a (right-linear) or A -> Ba or A -> a (left-linear)

    This class follows SRP - it only handles grammar operations,
    not conversion to automata (that's handled by converters).
    """

    def __init__(self, vn: Set[str], vt: Set[str], productions: Dict[str, List[str]]):
        """
        Initialize a Regular Grammar.

        Args:
            vn: Set of non-terminal symbols (e.g., {'S', 'A', 'B'})
            vt: Set of terminal symbols (e.g., {'a', 'b'})
            productions: Dictionary mapping non-terminals to lists of productions
                        (e.g., {'S': ['aA', 'b'], 'A': ['a', 'bB']})
        """
        super().__init__(vn, vt, productions)
        # Ensure start symbol 'S' exists
        if "S" not in self.productions:
            raise ValueError("Grammar must have start symbol 'S' in productions")

    def get_chomsky_type(self) -> int:
        """
        Determine the Chomsky hierarchy type.

        Returns:
            3 = Regular (Type 3)
            2 = Context-Free (Type 2)
            1 = Context-Sensitive (Type 1)
            0 = Unrestricted (Type 0)
        """
        # Type 3: Regular Grammar checks
        # All productions must be: A -> aB, A -> a, A -> ε (right-linear)
        # or: A -> Ba, A -> a, A -> ε (left-linear)

        for non_terminal, rules in self.productions.items():
            # Multiple characters in LHS not allowed for Type 3+
            if len(non_terminal) > 1:
                return 1  # Could be Type 1 or 0

            for rule in rules:
                # Empty production is allowed in regular grammar
                if rule == "" or rule == "ε":
                    continue

                # Count non-terminals in the rule
                non_terminal_count = sum(1 for char in rule if char.isupper())

                # More than one non-terminal -> Type 2 or below
                if non_terminal_count > 1:
                    return 2

                # Check position of non-terminal (must be at start or end for Type 3)
                if non_terminal_count == 1:
                    if rule.isupper():
                        return 2  # Single non-terminal, could be Type 2

                    # For right-linear: non-terminal should be at the END
                    # For left-linear: non-terminal should be at the START
                    has_terminal_first = rule[0].islower() if len(rule) > 0 else False
                    has_terminal_last = rule[-1].islower() if len(rule) > 0 else False

                    # If we have A -> aB (terminal then non-terminal) - right linear OK
                    # If we have A -> Ba (non-terminal then terminal) - left linear OK
                    if not (has_terminal_last or has_terminal_first):
                        return 2

        return 3  # Type 3 - Regular Grammar

    def generate_word(self, max_length: int = 20) -> str:
        """
        Generate a random word from the grammar.

        Args:
            max_length: Maximum length of generated word to prevent infinite loops

        Returns:
            A string generated from the grammar

        Raises:
            RuntimeError: If max_length exceeded
        """
        current = "S"
        result = []
        iterations = 0
        max_iterations = max_length * 2  # Safety limit

        while iterations < max_iterations:
            iterations += 1

            # Get productions for current non-terminal
            if current not in self.productions:
                break

            # Pick random production
            production = random.choice(self.productions[current])

            if not production or production == "ε":
                # Empty production means we're done
                break

            # Separate terminals and non-terminals
            for char in production:
                if char.islower():
                    result.append(char)
                else:
                    current = char

        if iterations >= max_iterations:
            raise RuntimeError(
                f"Failed to generate word within {max_length} characters"
            )

        return "".join(result)

    def __repr__(self) -> str:
        return f"RegularGrammar(VN={self.vn}, VT={self.vt}, Productions={self.productions})"
