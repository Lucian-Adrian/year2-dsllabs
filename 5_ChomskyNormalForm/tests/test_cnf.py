from __future__ import annotations

from pathlib import Path

from src.catalog import list_variants, load_variant_grammar
from src.cnf import CNFConverter
from src.grammar import Grammar
from src.reporting import write_report_bundle


def test_variant_catalog_has_32_entries() -> None:
    variants = list_variants()
    assert len(variants) == 32
    assert variants[0] == 1
    assert variants[-1] == 32


def test_variant_13_catalog_entry_is_complete() -> None:
    grammar = load_variant_grammar(13)
    assert grammar.start_symbol == "S"
    assert grammar.production_count() == 10
    assert grammar.productions[0].lhs == "S"
    assert grammar.productions[0].rhs == ("a", "B")


def test_variant_13_converts_to_cnf() -> None:
    grammar = load_variant_grammar(13)
    result = CNFConverter().convert(grammar)
    assert result.is_valid()
    assert result.final.is_cnf()
    assert result.final.start_symbol in result.final.non_terminals
    assert len(result.steps) >= 5


def test_nullable_and_unit_pipeline_handles_epsilon_and_renaming() -> None:
    grammar = Grammar.from_text(
        """
        S -> A | ε
        A -> B
        B -> a
        """
    )
    result = CNFConverter().convert(grammar)
    assert result.is_valid()
    assert result.final.is_cnf()
    assert any(not production.rhs for production in result.final.productions)


def test_binarization_breaks_long_rules() -> None:
    grammar = Grammar.from_text(
        """
        S -> A B C D
        A -> a
        B -> b
        C -> c
        D -> d
        """
    )
    result = CNFConverter().convert(grammar)
    assert result.is_valid()
    assert max(len(production.rhs) for production in result.final.productions) <= 2


def test_report_bundle_writes_artifacts(tmp_path: Path) -> None:
    grammar = load_variant_grammar(13)
    result = CNFConverter().convert(grammar)
    bundle = tmp_path / "bundle"
    write_report_bundle(bundle, "Variant 13", grammar, result)
    assert (bundle / "report.md").exists()
    assert (bundle / "original.mmd").exists()
    assert (bundle / "pipeline.mmd").exists()
    assert (bundle / "final.mmd").exists()
    assert (bundle / "result.json").exists()
