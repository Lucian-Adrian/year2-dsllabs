"""
Powerset (Subset) Construction — Layer 4: The Powerset Compiler.

Algorithm complexity:  O(2^n) worst-case for state explosion,
                       O(n) per produced DFA state traversal.

Each macro-state of the DFA is a frozenset of NDFA states.
If the NDFA has n states, the DFA has at most 2^n macro-states,
but in practice far fewer are reachable from the start state.
"""

from __future__ import annotations

from collections import deque
from typing import Dict, FrozenSet, List, Set, Tuple

from .ndfa import NDFA


# ---------------------------------------------------------------------------
# Lightweight DFA representation (returned by the compiler)
# ---------------------------------------------------------------------------

class DFA:
    """A deterministic finite automaton produced by powerset construction."""

    DEAD_LABEL = "∅"

    def __init__(
        self,
        states: List[str],
        alphabet: List[str],
        transitions: Dict[Tuple[str, str], str],
        start: str,
        accepting: Set[str],
        # Keep original frozenset mapping for visualiser colouring
        macro_map: Dict[str, FrozenSet[str]],
    ) -> None:
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start = start
        self.accepting: Set[str] = accepting
        self.macro_map = macro_map  # label → frozenset of original NDFA states

    # ------------------------------------------------------------------
    # String validation (O(n) in input length)
    # ------------------------------------------------------------------

    def check(self, input_string: str) -> bool:
        state = self.start
        for ch in input_string:
            state = self.transitions.get((state, ch), self.DEAD_LABEL)
        return state in self.accepting

    def trace(self, input_string: str) -> Tuple[bool, List[str]]:
        """Return (accepted, [state path]) for step-by-step debugging/highlighting."""
        path = [self.start]
        state = self.start
        for ch in input_string:
            state = self.transitions.get((state, ch), self.DEAD_LABEL)
            path.append(state)
        return state in self.accepting, path

    # ------------------------------------------------------------------
    # FA → Grammar (right-linear, for the reverse-engineer layer)
    # ------------------------------------------------------------------

    def to_grammar(self) -> List[Tuple[str, str]]:
        """Extract right-linear productions from the DFA (same algorithm as NDFA)."""
        productions: List[Tuple[str, str]] = []
        for (qi, c), qj in self.transitions.items():
            if qj == self.DEAD_LABEL:
                continue
            if qj in self.accepting:
                productions.append((qi, c))
            productions.append((qi, f"{c} {qj}"))
        for state in self.accepting:
            productions.append((state, ""))
        seen: set = set()
        unique = []
        for p in productions:
            if p not in seen:
                seen.add(p)
                unique.append(p)
        return unique

    def __repr__(self) -> str:
        return (
            f"<DFA states={len(self.states)} alpha={self.alphabet} "
            f"start={self.start!r} accepting={sorted(self.accepting)}>"
        )


# ---------------------------------------------------------------------------
# Powerset construction
# ---------------------------------------------------------------------------

def label(macro: FrozenSet[str]) -> str:
    """Convert a frozenset of NDFA states into a readable DFA state label."""
    if not macro:
        return DFA.DEAD_LABEL
    return "{" + ",".join(sorted(macro)) + "}"


def powerset_construction(ndfa: NDFA, include_dead: bool = True) -> DFA:
    """
    Collapse NDFA uncertainty into a DFA using the subset/powerset construction.

    Parameters
    ----------
    ndfa         : source NDFA
    include_dead : if True, include the dead (trap) state ∅ explicitly

    Returns
    -------
    DFA instance with human-readable macro-state labels.

    Also captures the construction table (steps) as ndfa.construction_table
    so the dashboard can render the step-by-step proof.
    """
    start_macro: FrozenSet[str] = frozenset({ndfa.start})

    # BFS over macro-states
    visited: Dict[FrozenSet[str], str] = {}
    queue: deque[FrozenSet[str]] = deque([start_macro])
    visited[start_macro] = label(start_macro)

    dfa_transitions: Dict[Tuple[str, str], str] = {}
    construction_steps: List[Dict] = []   # for dashboard display

    while queue:
        macro = queue.popleft()
        macro_lbl = visited[macro]

        step: Dict = {
            "macro_state": macro_lbl,
            "transitions": {},
        }

        for sym in ndfa.alphabet:
            # Union of all δ(qi, sym) for qi in macro
            nxt: FrozenSet[str] = frozenset(
                t for qi in macro for t in ndfa.delta(qi, sym)
            )

            if not nxt and not include_dead:
                step["transitions"][sym] = "—"
                continue

            nxt_lbl = label(nxt)
            dfa_transitions[(macro_lbl, sym)] = nxt_lbl
            step["transitions"][sym] = nxt_lbl

            if nxt not in visited:
                visited[nxt] = nxt_lbl
                queue.append(nxt)

        construction_steps.append(step)

    # Determine DFA accepting states: any macro that contains an NDFA accepting state
    dfa_accepting: Set[str] = {
        lbl for macro, lbl in visited.items() if macro & ndfa.accepting
    }

    dfa_states = list(visited.values())
    if include_dead and DFA.DEAD_LABEL not in dfa_states:
        # Add dead state self-loops if it was referenced
        for sym in ndfa.alphabet:
            if (DFA.DEAD_LABEL, sym) in dfa_transitions:
                if DFA.DEAD_LABEL not in dfa_states:
                    dfa_states.append(DFA.DEAD_LABEL)

    dfa = DFA(
        states=dfa_states,
        alphabet=ndfa.alphabet,
        transitions=dfa_transitions,
        start=visited[start_macro],
        accepting=dfa_accepting,
        macro_map=visited,
    )

    # Attach the construction table to the DFA object for dashboard use
    dfa.construction_steps = construction_steps  # type: ignore[attr-defined]

    return dfa
