from typing import Dict, List, Set, Tuple


class Automaton:
    def __init__(
        self,
        states: List[str],
        transitions: Dict[Tuple[str, str], str],
        start_state: str,
        accepting_states: List[str],
    ) -> None:
        self.states: Set[str] = set(states)
        self.transitions: Dict[Tuple[str, str], str] = transitions
        self.start_state: str = start_state
        self.accepting_states: Set[str] = set(accepting_states)

    def check(self, input_string: str) -> bool:
        """Check if the input string is accepted by the automaton."""
        current_state = self.start_state
        for token in input_string:
            if (current_state, token) not in self.transitions:
                return False
            current_state = self.transitions[(current_state, token)]
        return current_state in self.accepting_states

    def check_with_path(self, input_string: str) -> Tuple[bool, List[str]]:
        """Check acceptance and return the path of states for debugging invalid strings."""
        path = [self.start_state]
        current_state = self.start_state
        for token in input_string:
            if (current_state, token) not in self.transitions:
                return False, path + ["REJECTED"]
            current_state = self.transitions[(current_state, token)]
            path.append(current_state)
        accepted = current_state in self.accepting_states
        return accepted, path
