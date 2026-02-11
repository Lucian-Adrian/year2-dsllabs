import json
import random
from typing import Any, Dict, List, Tuple

from .automaton import Automaton


class Production:
    def __init__(self, source_state: str, production: str) -> None:
        self.source_state: str = source_state
        self.production: str = production


class Grammar:
    VIRTUAL_FINAL_STATE: str = "Ω"

    def __init__(self, grammar_definition_path: str) -> None:
        with open(grammar_definition_path, "r") as file:
            grammar_definition: Dict[str, Any] = json.load(file)

        self.non_terminals: List[str] = grammar_definition["non_terminals"]
        self.terminals: List[str] = grammar_definition["terminals"]
        self.start: str = grammar_definition["start"]

        # Convert rules to Production objects
        self.productions: List[Production] = [
            Production(rule["from"], rule["to"]) for rule in grammar_definition["rules"]
        ]

        # Group productions by source state for O(1) lookup
        self.production_map: Dict[str, List[Production]] = {}
        for prod in self.productions:
            if prod.source_state not in self.production_map:
                self.production_map[prod.source_state] = []
            self.production_map[prod.source_state].append(prod)

    def sample(self) -> str:
        """Generate a single string by recursively sampling from the grammar."""
        return self._recursively_sample(self.start)

    def _recursively_sample(self, current_state: str) -> str:
        if current_state in self.terminals:
            return current_state

        # Find productions for this state using O(1) lookup
        possible_productions = self.production_map.get(current_state, [])
        if not possible_productions:
            raise ValueError(f"No productions for state {current_state}")

        # Pick a random production
        chosen_production = random.choice(possible_productions)

        # Expand each token in the production
        result = ""
        for token in chosen_production.production:
            if token in self.non_terminals:
                result += self._recursively_sample(token)
            else:
                result += token
        return result

    def build_finite_automaton(self) -> Automaton:
        """Build a Finite Automaton from the grammar."""
        states = self._identify_states()
        transitions: Dict[Tuple[str, str], str] = {}

        for production in self.productions:
            source_state, input_token, target_state = self._parse_transition(production)
            transitions[(source_state, input_token)] = target_state

        # Add transitions to final state for terminal-only productions
        accepting_states = [self.VIRTUAL_FINAL_STATE]

        return Automaton(states, transitions, self.start, accepting_states)

    def _identify_states(self) -> List[str]:
        """Identify all unique states from non-terminals and add virtual final state."""
        states = set(self.non_terminals)
        states.add(self.VIRTUAL_FINAL_STATE)
        return list(states)

    def _parse_transition(self, production: Production) -> Tuple[str, str, str]:
        """Parse a production rule into (source_state, input_token, target_state)."""
        source_state = production.source_state
        production_str = production.production

        if len(production_str) == 1:
            # Terminal only, go to final state
            input_token = production_str
            target_state = self.VIRTUAL_FINAL_STATE
        elif len(production_str) == 2:
            # Terminal + Non-terminal
            input_token = production_str[0]
            target_state = production_str[1]
        else:
            raise ValueError(f"Invalid production length: {production_str}")

        return source_state, input_token, target_state
