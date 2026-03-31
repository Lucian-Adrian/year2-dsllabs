from __future__ import annotations

import re

from src.generator import explain_generation, generate_language, to_python_regex
from src.parser import normalize_expression, parse_regex
from src.variants import TASK_EXAMPLES, VARIANTS
from src.visualization import ast_metrics, ast_to_mermaid, generation_trace_to_mermaid


def _compiled(expr: str) -> re.Pattern[str]:
    node = parse_regex(expr)
    return re.compile(f"^{to_python_regex(node)}$")


def test_all_variant_patterns_parse() -> None:
    for variant in VARIANTS.values():
        for expression in variant.expressions:
            parse_regex(expression)


def test_given_task_examples_match_interpreted_variants() -> None:
    for variant_id, variant in VARIANTS.items():
        examples_for_variant = TASK_EXAMPLES[variant_id]
        for expression, examples in zip(variant.expressions, examples_for_variant):
            pattern = _compiled(expression)
            for sample in examples:
                assert pattern.fullmatch(sample) is not None


def test_generated_words_match_python_regex_engine() -> None:
    for variant in VARIANTS.values():
        for expression in variant.expressions:
            node = parse_regex(expression)
            pattern = _compiled(expression)
            generated = generate_language(node, max_repeat=5, max_results=30)
            assert generated
            for word in generated:
                assert pattern.fullmatch(word) is not None


def test_star_generation_respects_repeat_limit() -> None:
    node = parse_regex("A*")
    generated = generate_language(node, max_repeat=5, max_results=20)
    assert generated == ["", "A", "AA", "AAA", "AAAA", "AAAAA"]


def test_bonus_trace_returns_steps_and_valid_word() -> None:
    expression = "J+K(L|M|N)*O?(P|Q)^3"
    word, steps = explain_generation(expression, max_repeat=5, seed=7)
    assert word
    assert steps

    pattern = _compiled(expression)
    assert pattern.fullmatch(word) is not None


def test_unicode_superscript_normalization() -> None:
    expression = "(A|B)" + chr(0x00B2) + "C" + chr(0x2075)
    assert normalize_expression(expression) == "(A|B)^2C^5"


def test_visualization_mermaid_outputs_have_expected_sections() -> None:
    node = parse_regex("A(B|C)+D?")
    diagram = ast_to_mermaid(node, title="demo")
    assert "flowchart TD" in diagram
    assert "Regex Root" in diagram
    assert "Alternation" in diagram


def test_trace_mermaid_and_metrics_are_non_empty() -> None:
    expression = "J+K(L|M|N)*O?(P|Q)^3"
    word, steps = explain_generation(expression, max_repeat=5, seed=9)
    trace_diagram = generation_trace_to_mermaid(word, steps)
    assert "flowchart LR" in trace_diagram
    assert "output:" in trace_diagram

    metrics = ast_metrics(parse_regex(expression), max_repeat=5)
    assert metrics["nodes"] > 0
    assert metrics["depth"] > 0
    assert metrics["rough_paths"] > 0
