"""
Generic Grammar — Layer 2: The Chomsky Linter.

This module accepts any set of production rules and mathematically proves
their Chomsky hierarchy classification by analysing the algebraic structure
of each LHS and RHS.

Productions are stored as (LHS, RHS) pairs where each side is a
space-separated sequence of symbol names.  An empty RHS string represents ε.

Chomsky Hierarchy
-----------------
Type 3  Regular       : LHS is a single non-terminal; RHS is ε, a single
                        terminal, or exactly (terminal non-terminal) [right-
                        linear] or (non-terminal terminal) [left-linear].
                        All productions must share the same linearity direction.
Type 2  Context-Free  : LHS is a single non-terminal; RHS is unrestricted.
Type 1  Context-Sens. : |LHS| ≤ |RHS| for all productions (S→ε allowed if S
                        does not appear on any RHS).
Type 0  Unrestricted  : Anything else.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Set, Tuple


@dataclass
class Grammar:
    """A formal grammar defined by its alphabet sets and production rules."""

    non_terminals: Set[str]
    terminals: Set[str]
    start: str
    # productions: list of (LHS_string, RHS_string)
    productions: List[Tuple[str, str]] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Factory: build from FA-derived (LHS, RHS) pairs
    # ------------------------------------------------------------------

    @classmethod
    def from_fa_productions(
        cls,
        non_terminals: Set[str],
        terminals: Set[str],
        start: str,
        productions: List[Tuple[str, str]],
    ) -> "Grammar":
        return cls(
            non_terminals=non_terminals,
            terminals=terminals,
            start=start,
            productions=productions,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _symbols(self, side: str) -> List[str]:
        """Split a space-separated side into a list of symbol names."""
        return side.split() if side.strip() else []

    def _is_nt(self, sym: str) -> bool:
        return sym in self.non_terminals

    def _is_t(self, sym: str) -> bool:
        return sym in self.terminals

    # ------------------------------------------------------------------
    # Task 2a — Chomsky Classification
    # ------------------------------------------------------------------

    def classify_chomsky(self) -> Tuple[int, str, List[str]]:
        """
        Return (type_number, label, [evidence lines]) for this grammar.

        The evidence lines explain *why* each type check passed or failed,
        providing a mathematical proof suitable for a report.
        """
        evidence: List[str] = []
        # Track linearity: None, "right", "left", "mixed"
        linearity: str | None = None

        is_type_3 = True
        is_type_2 = True
        is_type_1 = True

        for lhs, rhs in self.productions:
            lhs_syms = self._symbols(lhs)
            rhs_syms = self._symbols(rhs)

            lhs_len = len(lhs_syms) if lhs_syms else 0
            rhs_len = len(rhs_syms) if rhs_syms else 0

            # ---- Type 2 / Type 3 require a single NT on LHS
            single_nt_lhs = (lhs_len == 1 and self._is_nt(lhs_syms[0]))

            if not single_nt_lhs:
                is_type_3 = False
                is_type_2 = False
                evidence.append(
                    f"  Type 2 FAIL: LHS {lhs!r} is not a single non-terminal "
                    f"in production {lhs!r} → {rhs!r}"
                )
                # Check Type 1: |LHS| ≤ |RHS|
                if lhs_len > rhs_len:
                    is_start_eps = (
                        lhs_syms == [self.start]
                        and rhs_syms == []
                        and not any(
                            self.start in self._symbols(r)
                            for _, r in self.productions
                        )
                    )
                    if not is_start_eps:
                        is_type_1 = False
                        evidence.append(
                            f"  Type 1 FAIL: |LHS|={lhs_len} > |RHS|={rhs_len} "
                            f"in production {lhs!r} → {rhs!r}"
                        )
                continue

            # LHS is a single NT — Type 2 is still possible.
            # For Type 1 with single NT, |LHS|=1 ≥ |RHS|=0 (epsilon) is a special case:
            # ε from a single NT is valid in Type 3 (regular) and Type 2 (context-free).

            # ---- Type 3 check: right-linear or left-linear structure
            if rhs_syms == []:
                pass  # ε from accepting states is valid for regular grammars
            elif len(rhs_syms) == 1 and self._is_t(rhs_syms[0]):
                pass  # single terminal: valid for both directions
            elif (
                len(rhs_syms) == 2
                and self._is_t(rhs_syms[0])
                and self._is_nt(rhs_syms[1])
            ):
                # right-linear
                if linearity == "left":
                    linearity = "mixed"
                    is_type_3 = False
                    evidence.append(
                        f"  Type 3 FAIL: mixed linearity — "
                        f"right-linear production {lhs!r} → {rhs!r} "
                        f"conflicts with earlier left-linear production."
                    )
                else:
                    linearity = "right"
            elif (
                len(rhs_syms) == 2
                and self._is_nt(rhs_syms[0])
                and self._is_t(rhs_syms[1])
            ):
                # left-linear
                if linearity == "right":
                    linearity = "mixed"
                    is_type_3 = False
                    evidence.append(
                        f"  Type 3 FAIL: mixed linearity — "
                        f"left-linear production {lhs!r} → {rhs!r} "
                        f"conflicts with earlier right-linear production."
                    )
                else:
                    linearity = "left"
            else:
                is_type_3 = False
                evidence.append(
                    f"  Type 3 FAIL: RHS {rhs!r} does not match any regular "
                    f"grammar pattern in production {lhs!r} → {rhs!r}"
                )

        # ---- Determine final type
        if is_type_3:
            direction = f" ({linearity}-linear)" if linearity else ""
            evidence.insert(0, f"✔ All productions match right/left-linear pattern{direction}.")
            return 3, "Type 3 — Regular Grammar", evidence

        if is_type_2:
            evidence.insert(0, "✔ All LHS are single non-terminals (context-free).")
            return 2, "Type 2 — Context-Free Grammar", evidence

        if is_type_1:
            evidence.insert(0, "✔ All productions satisfy |LHS| ≤ |RHS| (context-sensitive).")
            return 1, "Type 1 — Context-Sensitive Grammar", evidence

        evidence.insert(0, "✘ Grammar does not satisfy constraints for Types 1–3.")
        return 0, "Type 0 — Unrestricted Grammar", evidence

    # ------------------------------------------------------------------
    # Pretty-print
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        lines = [
            f"Grammar(NT={sorted(self.non_terminals)}, T={sorted(self.terminals)}, S={self.start!r})",
            "Productions:",
        ]
        for lhs, rhs in self.productions:
            lines.append(f"  {lhs} → {rhs if rhs else 'ε'}")
        return "\n".join(lines)
