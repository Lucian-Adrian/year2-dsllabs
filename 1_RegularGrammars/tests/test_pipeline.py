import pytest
from src.automaton import Automaton
from src.grammar import Grammar


@pytest.fixture
def grammar():
    return Grammar("config/variant_13.json")


@pytest.fixture
def automaton(grammar):
    return grammar.build_finite_automaton()


def test_grammar_loads_correctly(grammar):
    assert grammar.start == "S"
    assert "S" in grammar.non_terminals
    assert "a" in grammar.terminals
    assert len(grammar.productions) == 7  # Based on variant


def test_sample_generates_valid_string(grammar):
    sample = grammar.sample()
    assert isinstance(sample, str)
    assert all(c in grammar.terminals for c in sample)
    # Check it's accepted by automaton
    fa = grammar.build_finite_automaton()
    assert fa.check(sample)


def test_automaton_accepts_generated_strings(grammar, automaton):
    for _ in range(10):
        sample = grammar.sample()
        assert automaton.check(sample)


def test_automaton_rejects_invalid_strings(automaton):
    invalid_strings = ["x", "abx", "aaa", ""]  # Assuming these are invalid
    for s in invalid_strings:
        assert not automaton.check(s)


def test_conversion_creates_valid_automaton(grammar, automaton):
    assert automaton.start_state == "S"
    assert "Ω" in automaton.states  # Virtual final state
    assert "Ω" in automaton.accepting_states
    # Check some transitions exist
    assert len(automaton.transitions) > 0


def test_path_tracing(automaton):
    sample = "aac"  # Known valid
    accepted, path = automaton.check_with_path(sample)
    assert accepted
    assert len(path) == len(sample) + 1  # States for each char + start


def test_invalid_path_tracing(automaton):
    invalid = "xyz"
    accepted, path = automaton.check_with_path(invalid)
    assert not accepted
    assert "REJECTED" in path
