from __future__ import annotations

import argparse
import importlib
import random
import re
import sys
from pathlib import Path
from typing import Iterable

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

_generator_mod = importlib.import_module("src.generator")
_parser_mod = importlib.import_module("src.parser")
_variants_mod = importlib.import_module("src.variants")
_visualization_mod = importlib.import_module("src.visualization")

explain_generation = _generator_mod.explain_generation
generate_language = _generator_mod.generate_language
generate_random_word = _generator_mod.generate_random_word
to_python_regex = _generator_mod.to_python_regex
parse_regex = _parser_mod.parse_regex
TASK_EXAMPLES = _variants_mod.TASK_EXAMPLES
VARIANTS = _variants_mod.VARIANTS
ast_metrics = _visualization_mod.ast_metrics
ast_to_mermaid = _visualization_mod.ast_to_mermaid
generation_trace_to_mermaid = _visualization_mod.generation_trace_to_mermaid
regex_pipeline_mermaid = _visualization_mod.regex_pipeline_mermaid


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dynamic regular-expression generator for all Lab 4 variants."
    )
    parser.add_argument(
        "--variant",
        default="all",
        choices=["all", "1", "2", "3", "4"],
        help="Variant number to run, or all variants.",
    )
    parser.add_argument(
        "--regex",
        action="append",
        default=[],
        help="Custom regex expression (repeat flag to pass multiple expressions).",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=8,
        help="How many words to print per expression.",
    )
    parser.add_argument(
        "--max-repeat",
        type=int,
        default=5,
        help="Cap for unbounded repetition operators (* and +).",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=200,
        help="Internal cap for deterministic enumeration.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible sampling.",
    )
    parser.add_argument(
        "--show-steps",
        action="store_true",
        help="Show bonus processing sequence for one generated word.",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate generated words with Python's regex engine.",
    )
    parser.add_argument(
        "--export-mermaid-dir",
        default="",
        help="Optional output directory for Mermaid .mmd visuals.",
    )
    parser.add_argument(
        "--mission-brief",
        action="store_true",
        help="Print deep mission-style analysis and ML analogy metadata.",
    )
    return parser.parse_args()


def _format_set(words: Iterable[str]) -> str:
    return "{" + ", ".join(words) + "}"


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _print_mission_brief(expression: str, words: list[str], max_repeat: int) -> None:
    ast = parse_regex(expression)
    metrics = ast_metrics(ast, max_repeat=max_repeat)
    engine_pattern = f"^{to_python_regex(ast)}$"
    uniqueness = len(set(words)) / max(1, len(words))

    print("Mission brief:")
    print(
        "  - structural complexity: "
        f"nodes={metrics['nodes']}, depth={metrics['depth']}, "
        f"alternations={metrics['alternations']}, repeats={metrics['repeats']}"
    )
    print(f"  - bounded search-space proxy: <= {metrics['rough_paths']} candidate paths")
    print(f"  - deterministic validation target: {engine_pattern}")
    print(f"  - sample diversity (proxy): {uniqueness:.2f}")
    print("  - ML analogy: this behaves like constrained decoding with hard grammar")
    print(
        "    constraints, where alternations are branching decisions and repeat caps"
        " are decoding-time regularization."
    )
    print(
        "  - real-world utility: safe test-data generation for parsers, schema guards,"
        " and lexical protocol fuzzing."
    )


def _targets_from_args(args: argparse.Namespace) -> list[tuple[str, tuple[str, ...]]]:
    if args.regex:
        return [("custom", tuple(args.regex))]

    if args.variant == "all":
        return [
            (f"variant {variant_id}", VARIANTS[variant_id].expressions)
            for variant_id in sorted(VARIANTS)
        ]

    variant_id = int(args.variant)
    return [(f"variant {variant_id}", VARIANTS[variant_id].expressions)]


def _validate_samples(expression: str, words: list[str]) -> None:
    ast = parse_regex(expression)
    compiled = re.compile(f"^{to_python_regex(ast)}$")
    invalid = [word for word in words if compiled.fullmatch(word) is None]
    if invalid:
        raise RuntimeError(
            "Generation mismatch: sampled words do not match expression "
            f"{expression!r}: {invalid}"
        )


def _ensure_sample_count(
    expression: str,
    words: list[str],
    samples: int,
    max_repeat: int,
    rng: random.Random,
) -> list[str]:
    if len(words) >= samples:
        return words[:samples]

    ast = parse_regex(expression)
    seen = set(words)

    attempts = 0
    max_attempts = max(100, samples * 50)
    while len(words) < samples and attempts < max_attempts:
        attempts += 1
        candidate, _ = generate_random_word(ast, max_repeat=max_repeat, rng=rng)
        if candidate in seen:
            continue
        seen.add(candidate)
        words.append(candidate)

    return words[:samples]


def main() -> None:
    args = _parse_args()
    rng = random.Random(args.seed)
    targets = _targets_from_args(args)
    export_dir = Path(args.export_mermaid_dir) if args.export_mermaid_dir else None
    if export_dir is not None:
        export_dir.mkdir(parents=True, exist_ok=True)

    print("Regular Expressions Lab 4 - dynamic generator")
    print(f"seed={args.seed}, max_repeat={args.max_repeat}, samples={args.samples}")
    print()

    for label, expressions in targets:
        print(label.upper())
        print("-" * len(label))

        example_bucket = None
        if label.startswith("variant "):
            variant_id = int(label.split()[-1])
            example_bucket = TASK_EXAMPLES.get(variant_id)

        for index, expression in enumerate(expressions, start=1):
            ast = parse_regex(expression)
            words = generate_language(
                ast,
                max_repeat=args.max_repeat,
                max_results=max(args.max_results, args.samples),
            )
            words = _ensure_sample_count(
                expression,
                words,
                args.samples,
                args.max_repeat,
                rng,
            )

            if args.validate:
                _validate_samples(expression, words)

            print(f"Expression {index}: {expression}")
            print(f"Generated: {_format_set(words)}")

            if example_bucket and index <= len(example_bucket):
                print(f"Task examples: {_format_set(example_bucket[index - 1])}")

            trace_word = ""
            trace_steps = []
            if args.show_steps or export_dir is not None:
                sampled_word, steps = explain_generation(
                    expression,
                    max_repeat=args.max_repeat,
                    seed=rng.randint(0, 10_000_000),
                )
                trace_word, trace_steps = sampled_word, steps

            if args.show_steps:
                print(f"Trace sample: {sampled_word}")
                for step_number, step in enumerate(steps, start=1):
                    print(
                        f"  {step_number:02d}. path={step.path} "
                        f"action={step.action} detail={step.detail}"
                    )

            if args.mission_brief:
                _print_mission_brief(expression, words, args.max_repeat)

            if export_dir is not None:
                label_slug = _slug(label)
                base = f"{label_slug}_expr_{index}"

                ast_file = export_dir / f"{base}_ast.mmd"
                pipeline_file = export_dir / f"{base}_pipeline.mmd"
                trace_file = export_dir / f"{base}_trace.mmd"

                ast_file.write_text(
                    ast_to_mermaid(ast, title=f"{label} expression {index}"),
                    encoding="utf-8",
                )
                pipeline_file.write_text(regex_pipeline_mermaid(), encoding="utf-8")
                trace_file.write_text(
                    generation_trace_to_mermaid(trace_word, trace_steps),
                    encoding="utf-8",
                )
                print(
                    "Visuals exported: "
                    f"{ast_file.name}, {pipeline_file.name}, {trace_file.name}"
                )

            print()


if __name__ == "__main__":
    main()
