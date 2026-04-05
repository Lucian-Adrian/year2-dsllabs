from __future__ import annotations

import json
import random
import re
import time
from pathlib import Path
from typing import Iterable

from .generator import explain_generation, generate_language, generate_random_word, to_python_regex
from .parser import parse_regex
from .variants import TASK_EXAMPLES, VARIANTS
from .visualization import ast_metrics


def _format_set(words: Iterable[str]) -> str:
    return "{" + ", ".join(words) + "}"


def _resolve_targets(
    targets: list[tuple[str, tuple[str, ...]]] | None,
) -> list[tuple[str, tuple[str, ...]]]:
    if targets is not None:
        return targets

    return [
        (f"variant {variant_id}", VARIANTS[variant_id].expressions)
        for variant_id in sorted(VARIANTS)
    ]


def _official_examples_for(label: str, index: int) -> tuple[str, ...]:
    if not label.startswith("variant "):
        return ()

    variant_id = int(label.split()[-1])
    bucket = TASK_EXAMPLES.get(variant_id)
    if not bucket or index > len(bucket):
        return ()
    return bucket[index - 1]


def _ensure_sample_count(
    expression: str,
    words: list[str],
    sample_count: int,
    max_repeat: int,
    rng: random.Random,
) -> list[str]:
    if len(words) >= sample_count:
        return words[:sample_count]

    ast = parse_regex(expression)
    seen = set(words)
    attempts = 0
    max_attempts = max(100, sample_count * 50)

    while len(words) < sample_count and attempts < max_attempts:
        attempts += 1
        candidate, _ = generate_random_word(ast, max_repeat=max_repeat, rng=rng)
        if candidate in seen:
            continue
        seen.add(candidate)
        words.append(candidate)

    return words[:sample_count]


def _time_ms(fn, iterations: int) -> float:
    start = time.perf_counter()
    for _ in range(iterations):
        fn()
    elapsed = time.perf_counter() - start
    return (elapsed * 1000.0) / max(iterations, 1)


def _benchmark_expression(
    expression: str,
    *,
    max_repeat: int,
    max_results: int,
    benchmark_iterations: int,
) -> dict[str, float]:
    ast = parse_regex(expression)
    generated_once = generate_language(ast, max_repeat=max_repeat, max_results=max_results)
    pattern_text = f"^{to_python_regex(ast)}$"

    parse_ms = _time_ms(lambda: parse_regex(expression), benchmark_iterations)
    generate_ms = _time_ms(
        lambda: generate_language(ast, max_repeat=max_repeat, max_results=max_results),
        benchmark_iterations,
    )
    validate_ms = _time_ms(
        lambda: [
            re.fullmatch(pattern_text, word)
            for word in generated_once
        ],
        benchmark_iterations,
    )

    return {
        "parse_ms": round(parse_ms, 4),
        "generate_ms": round(generate_ms, 4),
        "validate_ms": round(validate_ms, 4),
    }


def _expression_analysis(
    *,
    label: str,
    index: int,
    expression: str,
    max_repeat: int,
    max_results: int,
    sample_count: int,
    seed: int,
    benchmark_iterations: int,
) -> dict[str, object]:
    ast = parse_regex(expression)
    metrics = ast_metrics(ast, max_repeat=max_repeat)
    python_regex = f"^{to_python_regex(ast)}$"

    rng = random.Random(seed)
    generated = generate_language(ast, max_repeat=max_repeat, max_results=max(max_results, sample_count))
    generated = _ensure_sample_count(expression, generated, sample_count, max_repeat, rng)
    trace_word, trace_steps = explain_generation(expression, max_repeat=max_repeat, seed=seed + 97)

    return {
        "index": index,
        "expression": expression,
        "python_regex": python_regex,
        "metrics": metrics,
        "generated": generated,
        "official_examples": list(_official_examples_for(label, index)),
        "trace": {
            "word": trace_word,
            "steps": [
                {"path": step.path, "action": step.action, "detail": step.detail}
                for step in trace_steps
            ],
        },
        "benchmark": _benchmark_expression(
            expression,
            max_repeat=max_repeat,
            max_results=max_results,
            benchmark_iterations=benchmark_iterations,
        ),
    }


def build_lab_analysis(
    *,
    max_repeat: int = 5,
    max_results: int = 200,
    sample_count: int = 8,
    seed: int = 42,
    benchmark_iterations: int = 10,
    targets: list[tuple[str, tuple[str, ...]]] | None = None,
) -> dict[str, object]:
    resolved_targets = _resolve_targets(targets)
    variants: list[dict[str, object]] = []

    expression_counter = 0
    path_total = 0
    max_path_entry: tuple[str, int, int] | None = None

    for variant_offset, (label, expressions) in enumerate(resolved_targets):
        expression_entries: list[dict[str, object]] = []
        for index, expression in enumerate(expressions, start=1):
            expression_counter += 1
            analysis = _expression_analysis(
                label=label,
                index=index,
                expression=expression,
                max_repeat=max_repeat,
                max_results=max_results,
                sample_count=sample_count,
                seed=seed + variant_offset * 100 + index,
                benchmark_iterations=benchmark_iterations,
            )
            rough_paths = int(analysis["metrics"]["rough_paths"])  # type: ignore[index]
            path_total += rough_paths
            if max_path_entry is None or rough_paths > max_path_entry[2]:
                max_path_entry = (label, index, rough_paths)
            expression_entries.append(analysis)

        variants.append({"label": label, "expressions": expression_entries})

    hottest = {
        "label": max_path_entry[0] if max_path_entry else "",
        "expression_index": max_path_entry[1] if max_path_entry else 0,
        "rough_paths": max_path_entry[2] if max_path_entry else 0,
    }

    return {
        "meta": {
            "variant_count": len(variants),
            "expression_count": expression_counter,
            "max_repeat": max_repeat,
            "sample_count": sample_count,
            "max_results": max_results,
            "benchmark_iterations": benchmark_iterations,
            "seed": seed,
            "rough_path_total": path_total,
            "heaviest_expression": hottest,
        },
        "variants": variants,
    }


def render_terminal_transcript(analysis: dict[str, object]) -> str:
    meta = analysis["meta"]  # type: ignore[index]
    variants = analysis["variants"]  # type: ignore[index]

    lines = [
        "Regular Expressions Lab 4 - analysis transcript",
        f"seed={meta['seed']}, max_repeat={meta['max_repeat']}, samples={meta['sample_count']}, benchmark_iterations={meta['benchmark_iterations']}",
        "",
    ]

    for variant in variants:
        lines.append(str(variant["label"]).upper())
        lines.append("-" * len(str(variant["label"])))
        for expression in variant["expressions"]:
            bench = expression["benchmark"]
            metrics = expression["metrics"]
            lines.append(f"Expression {expression['index']}: {expression['expression']}")
            lines.append(f"Generated: {_format_set(expression['generated'])}")
            if expression["official_examples"]:
                lines.append(f"Task examples: {_format_set(expression['official_examples'])}")
            lines.append(
                "Metrics: "
                f"nodes={metrics['nodes']}, depth={metrics['depth']}, "
                f"alternations={metrics['alternations']}, repeats={metrics['repeats']}, "
                f"rough_paths={metrics['rough_paths']}"
            )
            lines.append(
                "Benchmark: "
                f"parse_ms={bench['parse_ms']}, generate_ms={bench['generate_ms']}, "
                f"validate_ms={bench['validate_ms']}"
            )
            lines.append(f"Validation target: {expression['python_regex']}")
            lines.append(f"Trace sample: {expression['trace']['word']}")
            for step in expression["trace"]["steps"][:5]:
                lines.append(
                    f"  - path={step['path']} action={step['action']} detail={step['detail']}"
                )
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_analysis_markdown(analysis: dict[str, object]) -> str:
    meta = analysis["meta"]  # type: ignore[index]
    variants = analysis["variants"]  # type: ignore[index]
    hottest = meta["heaviest_expression"]

    lines = [
        "# Lab 4 Analysis Bundle",
        "",
        "## Meta",
        "",
        f"- Variants covered: {meta['variant_count']}",
        f"- Expressions covered: {meta['expression_count']}",
        f"- Repeat cap: {meta['max_repeat']}",
        f"- Sample count per expression: {meta['sample_count']}",
        f"- Benchmark iterations: {meta['benchmark_iterations']}",
        f"- Heaviest bounded expression: {hottest['label']} / expression {hottest['expression_index']} ({hottest['rough_paths']} rough paths)",
        "",
    ]

    for variant in variants:
        lines.append(f"## {variant['label'].title()}")
        lines.append("")
        for expression in variant["expressions"]:
            bench = expression["benchmark"]
            metrics = expression["metrics"]
            lines.append(f"### Expression {expression['index']}")
            lines.append("")
            lines.append(f"- Regex: `{expression['expression']}`")
            lines.append(f"- Validation target: `{expression['python_regex']}`")
            lines.append(
                f"- Metrics: nodes={metrics['nodes']}, depth={metrics['depth']}, alternations={metrics['alternations']}, repeats={metrics['repeats']}, rough_paths={metrics['rough_paths']}"
            )
            lines.append(
                f"- Benchmark: parse_ms={bench['parse_ms']}, generate_ms={bench['generate_ms']}, validate_ms={bench['validate_ms']}"
            )
            lines.append(f"- Generated samples: `{', '.join(expression['generated'])}`")
            if expression["official_examples"]:
                lines.append(f"- Official examples: `{', '.join(expression['official_examples'])}`")
            lines.append(f"- Trace sample: `{expression['trace']['word']}`")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_analysis_bundle(output_dir: str | Path, analysis: dict[str, object]) -> None:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    (destination / "summary.json").write_text(
        json.dumps(analysis, indent=2),
        encoding="utf-8",
    )
    (destination / "summary.md").write_text(
        render_analysis_markdown(analysis),
        encoding="utf-8",
    )
    (destination / "terminal_transcript.txt").write_text(
        render_terminal_transcript(analysis),
        encoding="utf-8",
    )
