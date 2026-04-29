from __future__ import annotations

import json
from pathlib import Path

from .cnf import CNFConversionResult
from .grammar import Grammar
from .visualization import grammar_mermaid, pipeline_mermaid


def _step_theory(step_title: str, step_description: str, notes: tuple[str, ...]) -> list[str]:
    title = step_title.lower()
    lines: list[str] = []

    if "augment start" in title:
        lines.append("This pass creates a fresh start symbol so later rewrites can freely eliminate ε-productions without breaking the CNF start-symbol rule.")
    elif "ε-productions" in title:
        lines.append("This pass expands nullable combinations so the language stays the same even after empty productions are removed.")
        lines.append("It works by enumerating every way nullable symbols can disappear from a right-hand side and keeping only the meaningful variants.")
    elif "unit productions" in title:
        lines.append("This pass removes renaming chains like A -> B -> C by directly copying the non-unit productions reachable through the chain.")
        lines.append("The language is preserved because unit edges only redirect to productions that already existed in the reachable closure.")
    elif "useless symbols" in title or "cleanup" in title:
        lines.append("This pass removes symbols that can never contribute to a terminal string and symbols that are unreachable from the start symbol.")
        lines.append("That shrinks the grammar before the CNF-specific rewrites, which makes the later passes easier to inspect.")
    elif "isolate terminals" in title:
        lines.append("This pass replaces terminals inside long right-hand sides with fresh pre-terminal helpers so the final grammar only uses terminals in length-1 rules.")
    elif "binarize" in title:
        lines.append("This pass rewrites long productions into a chain of binary rules, which is the structural requirement of Chomsky Normal Form.")
    else:
        lines.append(step_description)

    if notes:
        lines.append("Key observations from the converter:")
        lines.extend(f"- {note}" for note in notes)

    return lines


def build_report_markdown(title: str, grammar: Grammar, result: CNFConversionResult) -> str:
    lines: list[str] = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    lines.append(f"- Start symbol: `{grammar.start_symbol}`")
    lines.append(f"- Original productions: {grammar.production_count()}")
    lines.append(f"- Final productions: {result.final.production_count()}")
    lines.append(f"- Helper symbols introduced: {len(result.helper_symbols)}")
    lines.append(f"- Nullable symbols detected: {len(result.nullable_symbols)}")
    lines.append(f"- CNF check: {'passed' if result.is_valid() else 'failed'}")
    lines.append("")
    lines.append("## Pipeline")
    lines.append("")
    lines.append("```mermaid")
    lines.append(pipeline_mermaid(result))
    lines.append("```")
    lines.append("")
    lines.append("## Original Grammar")
    lines.append("")
    lines.append("```text")
    lines.append(grammar.pretty())
    lines.append("```")
    lines.append("")
    lines.append("## Final CNF")
    lines.append("")
    lines.append("```text")
    lines.append(result.final.pretty())
    lines.append("```")
    lines.append("")
    lines.append("## Step Summary")
    lines.append("")
    for step in result.steps:
        lines.append(f"### {step.title}")
        lines.append("")
        lines.append(step.description)
        lines.append("")
        lines.append("#### Theory")
        lines.append("")
        lines.extend(_step_theory(step.title, step.description, step.notes))
        lines.append("")
        if step.notes:
            lines.append("- Notes:")
            lines.extend(f"  - {note}" for note in step.notes)
            lines.append("")
        if step.added:
            lines.append("- Added:")
            lines.extend(f"  - {production}" for production in step.added[:8])
            if len(step.added) > 8:
                lines.append(f"  - ... +{len(step.added) - 8} more")
        if step.removed:
            lines.append("- Removed:")
            lines.extend(f"  - {production}" for production in step.removed[:8])
            if len(step.removed) > 8:
                lines.append(f"  - ... +{len(step.removed) - 8} more")
        lines.append("")
    lines.append("## Validation")
    lines.append("")
    if result.is_valid():
        lines.append("The final grammar satisfies Chomsky Normal Form.")
    else:
        lines.append("The final grammar still has issues:")
        lines.extend(f"- {issue}" for issue in result.issues)
    lines.append("")
    return "\n".join(lines)


def write_report_bundle(output_dir: str | Path, title: str, grammar: Grammar, result: CNFConversionResult) -> None:
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    (target / "report.md").write_text(build_report_markdown(title, grammar, result), encoding="utf-8")
    (target / "original.mmd").write_text(grammar_mermaid(grammar, f"{title} original grammar"), encoding="utf-8")
    (target / "pipeline.mmd").write_text(pipeline_mermaid(result), encoding="utf-8")
    (target / "final.mmd").write_text(grammar_mermaid(result.final, f"{title} final CNF"), encoding="utf-8")
    (target / "result.json").write_text(
        json.dumps(
            {
                "title": title,
                "original": grammar.summary(),
                "final": result.final.summary(),
                "issues": list(result.issues),
                "steps": [
                    {
                        "title": step.title,
                        "description": step.description,
                        "notes": list(step.notes),
                        "added": [str(prod) for prod in step.added],
                        "removed": [str(prod) for prod in step.removed],
                    }
                    for step in result.steps
                ],
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )