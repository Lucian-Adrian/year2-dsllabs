"""
NDFA (Non-Deterministic Finite Automaton) — Layer 3: State-Space Evaluator.

This module models an NDFA as a 5-tuple (Q, Σ, δ, q0, F) where δ maps
(state, symbol) → SET of states. A DFA is the special case where every
such set has exactly one element.
"""

from __future__ import annotations

import json
from collections import defaultdict
from typing import Dict, FrozenSet, List, Set, Tuple


class NDFA:
    """Represents a (non-)deterministic finite automaton loaded from a JSON config."""

    def __init__(
        self,
        states: List[str],
        alphabet: List[str],
        transitions: Dict[Tuple[str, str], Set[str]],
        start: str,
        accepting: List[str],
    ) -> None:
        self.states: List[str] = states
        self.alphabet: List[str] = alphabet
        # transitions: (state, symbol) → frozenset of target states
        self.transitions: Dict[Tuple[str, str], FrozenSet[str]] = {
            k: frozenset(v) for k, v in transitions.items()
        }
        self.start: str = start
        self.accepting: FrozenSet[str] = frozenset(accepting)

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def from_json(cls, path: str) -> "NDFA":
        """Load an NDFA definition from a JSON file (see config/variant_13_ndfa.json)."""
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)

        # Group multiple targets for the same (from, on) pair.
        raw: Dict[Tuple[str, str], Set[str]] = defaultdict(set)
        for t in data["transitions"]:
            raw[(t["from"], t["on"])].add(t["to"])

        return cls(
            states=data["states"],
            alphabet=data["alphabet"],
            transitions=dict(raw),
            start=data["start"],
            accepting=data["accepting"],
        )

    # ------------------------------------------------------------------
    # Task 3b — Determinism diagnostics
    # ------------------------------------------------------------------

    def is_deterministic(self) -> bool:
        """Return True if every (state, symbol) pair maps to at most one state."""
        return all(len(targets) <= 1 for targets in self.transitions.values())

    def non_deterministic_sources(self) -> List[Tuple[str, str]]:
        """Return all (state, symbol) pairs that cause non-determinism."""
        return [
            (state, sym)
            for (state, sym), targets in self.transitions.items()
            if len(targets) > 1
        ]

    # ------------------------------------------------------------------
    # Task 3a — Convert FA → Regular Grammar
    # ------------------------------------------------------------------

    def to_grammar(self) -> "list[tuple[str,str]]":
        """
        Extract right-linear productions from the automaton.

        Convention for each transition (qi, c) → qj:
          - If qj ∈ F (accepting)  : produce qi → c  (string may terminate here)
          - Always                  : produce qi → c qj  (continue processing)
          - For each qi ∈ F         : produce qi → ε  (allows acceptance from start if applicable)

        Returns a list of (LHS, RHS) string pairs where symbols are
        space-separated (suitable for the Chomsky classifier).
        """
        productions: List[Tuple[str, str]] = []

        for (qi, c), targets in self.transitions.items():
            for qj in sorted(targets):
                if qj in self.accepting:
                    # Terminal production — string can end here
                    productions.append((qi, c))
                # Always add the non-terminal continuation rule
                productions.append((qi, f"{c} {qj}"))

        # Epsilon productions for accepting states (handles ε-language membership)
        for state in self.accepting:
            productions.append((state, ""))

        # Deduplicate while preserving order
        seen: set = set()
        unique: List[Tuple[str, str]] = []
        for p in productions:
            if p not in seen:
                seen.add(p)
                unique.append(p)

        return unique

    # ------------------------------------------------------------------
    # Helpers used by visualizer and dashboard
    # ------------------------------------------------------------------

    def delta(self, state: str, symbol: str) -> FrozenSet[str]:
        """Return the (possibly empty) set of states reachable from state on symbol."""
        return self.transitions.get((state, symbol), frozenset())

    def run(self, input_string: str) -> bool:
        """Simulate the NDFA on input_string; return True if any execution accepts."""
        current: FrozenSet[str] = frozenset({self.start})
        for ch in input_string:
            nxt: Set[str] = set()
            for s in current:
                nxt |= self.delta(s, ch)
            current = frozenset(nxt)
        return bool(current & self.accepting)

    def __repr__(self) -> str:
        nd = "DFA" if self.is_deterministic() else "NDFA"
        return (
            f"<{nd} states={self.states} alpha={self.alphabet} "
            f"start={self.start!r} accepting={sorted(self.accepting)}>"
        )
