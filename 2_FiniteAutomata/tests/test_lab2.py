"""
Comprehensive test suite for Lab 2 — NDFA / DFA State-Space Compiler.

Tests cover:
  - NDFA loading and determinism detection (Task 3b)
  - FA → Regular Grammar extraction (Task 3a)
  - Chomsky classification of extracted grammar (Task 2a)
  - Powerset construction correctness (Task 3c)
  - DFA acceptance / rejection semantics
  - Edge cases: empty string, dead state, single-char strings
  - Consistency: NDFA.run() and DFA.check() must agree on every test string
"""

import pytest

from src.grammar import Grammar
from src.ndfa import NDFA
from src.powerset import DFA, powerset_construction


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def ndfa() -> NDFA:
    return NDFA.from_json("config/variant_13_ndfa.json")


@pytest.fixture(scope="module")
def dfa(ndfa: NDFA) -> DFA:
    return powerset_construction(ndfa, include_dead=True)


@pytest.fixture(scope="module")
def grammar(ndfa: NDFA) -> Grammar:
    prods = ndfa.to_grammar()
    return Grammar.from_fa_productions(
        non_terminals=set(ndfa.states),
        terminals=set(ndfa.alphabet),
        start=ndfa.start,
        productions=prods,
    )


# ---------------------------------------------------------------------------
# 1. NDFA Loading
# ---------------------------------------------------------------------------

class TestNDFALoading:
    def test_states_loaded(self, ndfa):
        assert set(ndfa.states) == {"q0", "q1", "q2", "q3"}

    def test_alphabet_loaded(self, ndfa):
        assert set(ndfa.alphabet) == {"a", "b"}

    def test_start_state(self, ndfa):
        assert ndfa.start == "q0"

    def test_accepting_state(self, ndfa):
        assert ndfa.accepting == frozenset({"q3"})

    def test_transition_count(self, ndfa):
        # 7 individual transition rules → grouped into 6 (state,sym) pairs
        # δ(q1,a)={q1,q2} is the merged pair
        total_entries = sum(len(v) for v in ndfa.transitions.values())
        assert total_entries == 7


# ---------------------------------------------------------------------------
# 2. Task 3b — Determinism Detection
# ---------------------------------------------------------------------------

class TestDeterminismDetection:
    def test_variant_13_is_not_deterministic(self, ndfa):
        assert ndfa.is_deterministic() is False

    def test_conflict_at_q1_on_a(self, ndfa):
        conflicts = ndfa.non_deterministic_sources()
        assert ("q1", "a") in conflicts

    def test_no_other_conflicts(self, ndfa):
        conflicts = ndfa.non_deterministic_sources()
        assert len(conflicts) == 1

    def test_pure_dfa_is_deterministic(self):
        """A simple DFA-like NDFA with no ambiguity should report deterministic."""
        from collections import defaultdict
        raw = defaultdict(set)
        raw[("s", "a")].add("t")
        raw[("t", "b")].add("s")
        simple = NDFA(
            states=["s", "t"],
            alphabet=["a", "b"],
            transitions=dict(raw),
            start="s",
            accepting=["t"],
        )
        assert simple.is_deterministic() is True


# ---------------------------------------------------------------------------
# 3. Task 3a — FA to Grammar
# ---------------------------------------------------------------------------

class TestFAToGrammar:
    def test_productions_are_non_empty(self, ndfa):
        prods = ndfa.to_grammar()
        assert len(prods) > 0

    def test_all_lhs_are_states(self, ndfa):
        prods = ndfa.to_grammar()
        states = set(ndfa.states) | {ndfa.start}
        for lhs, _ in prods:
            assert lhs in states

    def test_no_duplicate_productions(self, ndfa):
        prods = ndfa.to_grammar()
        assert len(prods) == len(set(prods))

    def test_contains_terminal_production_for_q1(self, ndfa):
        """q1 can read 'b' and go to accepting q3, so should produce q1 → b."""
        prods = ndfa.to_grammar()
        assert ("q1", "b") in prods

    def test_contains_terminal_production_for_q2(self, ndfa):
        """q2 can read 'b' and go to accepting q3, so should produce q2 → b."""
        prods = ndfa.to_grammar()
        assert ("q2", "b") in prods

    def test_epsilon_for_accepting_state(self, ndfa):
        """q3 is accepting, so grammar should include q3 → ε."""
        prods = ndfa.to_grammar()
        assert ("q3", "") in prods


# ---------------------------------------------------------------------------
# 4. Task 2a — Chomsky Classification
# ---------------------------------------------------------------------------

class TestChomskyClassification:
    def test_grammar_from_ndfa_is_type_3(self, grammar):
        type_num, label, _ = grammar.classify_chomsky()
        assert type_num == 3

    def test_label_contains_regular(self, grammar):
        _, label, _ = grammar.classify_chomsky()
        assert "Regular" in label

    def test_type_2_grammar(self):
        """Context-Free but not regular: A → B A."""
        g = Grammar(
            non_terminals={"A", "B"},
            terminals={"a", "b"},
            start="A",
            productions=[("A", "B A"), ("B", "b")],
        )
        type_num, _, _ = g.classify_chomsky()
        assert type_num == 2

    def test_type_1_grammar(self):
        """Context-Sensitive: AB → BA (|LHS|=2, |RHS|=2)."""
        g = Grammar(
            non_terminals={"A", "B"},
            terminals={"a", "b"},
            start="A",
            productions=[("A B", "B A"), ("A", "a"), ("B", "b")],
        )
        type_num, _, _ = g.classify_chomsky()
        assert type_num == 1

    def test_type_0_grammar(self):
        """Unrestricted: AB → a (|LHS|=2 > |RHS|=1 and not S→ε exception)."""
        g = Grammar(
            non_terminals={"A", "B"},
            terminals={"a"},
            start="A",
            productions=[("A B", "a"), ("A", "a")],
        )
        type_num, _, _ = g.classify_chomsky()
        assert type_num == 0

    def test_evidence_non_empty(self, grammar):
        _, _, evidence = grammar.classify_chomsky()
        assert len(evidence) > 0


# ---------------------------------------------------------------------------
# 5. Task 3c — Powerset Construction
# ---------------------------------------------------------------------------

class TestPowersetConstruction:
    def test_dfa_start_state_contains_ndfa_start(self, dfa, ndfa):
        assert ndfa.start in dfa.start

    def test_dfa_has_accepting_state(self, dfa, ndfa):
        assert len(dfa.accepting) > 0

    def test_accepting_state_contains_ndfa_accepting(self, dfa, ndfa):
        # macro_map is frozenset → label; reverse it to look up by label
        label_to_macro = {v: k for k, v in dfa.macro_map.items()}
        for acc in dfa.accepting:
            if acc != dfa.DEAD_LABEL:
                macro = label_to_macro.get(acc)
                if macro is not None:
                    assert bool(macro & ndfa.accepting)

    def test_dfa_is_actually_deterministic(self, dfa):
        """Each (state, symbol) in DFA transitions maps to exactly one state."""
        seen = {}
        for (state, sym), tgt in dfa.transitions.items():
            key = (state, sym)
            assert key not in seen, f"Duplicate transition: {key}"
            seen[key] = tgt

    def test_dfa_has_macro_state_for_q1_q2(self, dfa):
        """The non-determinism at q1 on 'a' must have resolved to a {q1,q2} macro-state."""
        state_labels = set(dfa.states)
        assert "{q1,q2}" in state_labels

    def test_construction_table_populated(self, dfa):
        table = dfa.construction_steps  # type: ignore[attr-defined]
        assert len(table) > 0

    def test_no_duplicate_states(self, dfa):
        assert len(dfa.states) == len(set(dfa.states))


# ---------------------------------------------------------------------------
# 6. DFA Acceptance Semantics
# ---------------------------------------------------------------------------

class TestDFAAcceptance:
    """
    Language of Variant 13 turns out to be: a* b a* b
    (zero or more a's, a b, zero or more a's, a b).
    """

    # --- Accepted strings ---
    def test_accepts_bb(self, dfa):
        assert dfa.check("bb") is True

    def test_accepts_abb(self, dfa):
        assert dfa.check("abb") is True

    def test_accepts_aabb(self, dfa):
        assert dfa.check("aabb") is True

    def test_accepts_bab(self, dfa):
        assert dfa.check("bab") is True

    def test_accepts_baab(self, dfa):
        assert dfa.check("baab") is True

    def test_accepts_abab(self, dfa):
        assert dfa.check("abab") is True

    def test_accepts_aababab(self, dfa):
        # a* b a* b → "aab" + "ab" → "aabab"
        assert dfa.check("aabab") is True

    # --- Rejected strings ---
    def test_rejects_empty(self, dfa):
        assert dfa.check("") is False

    def test_rejects_b_alone(self, dfa):
        assert dfa.check("b") is False

    def test_rejects_a_alone(self, dfa):
        assert dfa.check("a") is False

    def test_rejects_ba(self, dfa):
        assert dfa.check("ba") is False

    def test_rejects_bbb(self, dfa):
        assert dfa.check("bbb") is False

    def test_rejects_ababab(self, dfa):
        # Three alternating pairs — third 'b' hits dead state
        assert dfa.check("ababab") is False

    def test_rejects_character_not_in_alphabet(self, dfa):
        assert dfa.check("abxb") is False


# ---------------------------------------------------------------------------
# 7. NDFA / DFA Consistency
# ---------------------------------------------------------------------------

class TestNDFADFAConsistency:
    """NDFA.run() and DFA.check() must agree on all test strings."""

    STRINGS = [
        "bb", "abb", "bab", "baab", "aabb", "abab",
        "b", "a", "ba", "bbb", "ababab", "", "aaa",
        "aab", "aabbb",
    ]

    def test_consistency_on_all_strings(self, ndfa, dfa):
        for s in self.STRINGS:
            ndfa_result = ndfa.run(s)
            dfa_result = dfa.check(s)
            assert ndfa_result == dfa_result, (
                f"Mismatch on {s!r}: NDFA={ndfa_result}, DFA={dfa_result}"
            )


# ---------------------------------------------------------------------------
# 8. DFA Trace
# ---------------------------------------------------------------------------

class TestDFATrace:
    def test_trace_accepted_path_length(self, dfa):
        accepted, path = dfa.trace("bb")
        assert accepted is True
        assert len(path) == len("bb") + 1  # start + one state per character

    def test_trace_starts_at_dfa_start(self, dfa):
        _, path = dfa.trace("bab")
        assert path[0] == dfa.start

    def test_trace_ends_at_accepting(self, dfa):
        accepted, path = dfa.trace("bab")
        assert accepted is True
        assert path[-1] in dfa.accepting

    def test_trace_rejected_hits_dead_or_non_accepting(self, dfa):
        accepted, path = dfa.trace("b")
        assert accepted is False

    def test_trace_dead_state_label(self, dfa):
        _, path = dfa.trace("bbb")
        assert dfa.DEAD_LABEL in path
