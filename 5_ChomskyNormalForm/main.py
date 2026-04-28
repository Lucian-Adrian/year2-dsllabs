from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.catalog import list_variants, load_variant_grammar
from src.cnf import CNFConverter
from src.grammar import Grammar
from src.reporting import write_report_bundle


def _variant_choices() -> list[str]:
    return ["all"] + [str(variant_id) for variant_id in list_variants()]


def _slug(value: str) -> str:
    return "".join(char.lower() if char.isalnum() else "_" for char in value).strip("_")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lab 5 - Chomsky Normal Form converter")
    parser.add_argument(
        "--variant",
        default="13",
        choices=_variant_choices(),
        help="Official variant number to convert, or 'all' to process the complete catalog.",
    )
    parser.add_argument(
        "--grammar-file",
        default="",
        help="Optional custom grammar file (.json or plain text). Overrides --variant.",
    )
    parser.add_argument(
        "--export-dir",
        default="",
        help="Optional directory where a markdown report bundle and Mermaid visuals will be written.",
    )
    parser.add_argument(
        "--show-steps",
        action="store_true",
        help="Print a step-by-step trace of the CNF conversion.",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate the final grammar and return a non-zero exit code if CNF checks fail.",
    )
    parser.add_argument(
        "--list-variants",
        action="store_true",
        help="Print the available official variant ids and exit.",
    )
    return parser.parse_args()


def _load_custom_grammar(path: str) -> Grammar:
    return Grammar.from_file(path)


def _print_result(label: str, grammar: Grammar, result, show_steps: bool) -> None:
    print(label)
    print("=" * len(label))
    print(f"Original productions: {grammar.production_count()}")
    print(f"Final productions: {result.final.production_count()}")
    print(f"Helper symbols: {len(result.helper_symbols)}")
    print(f"Nullable symbols: {', '.join(result.nullable_symbols) if result.nullable_symbols else 'none'}")
    print(f"CNF check: {'passed' if result.is_valid() else 'failed'}")
    print()

    if show_steps:
        print("Original grammar:")
        print(grammar.pretty())
        print()
        for step in result.steps:
            print(step.title)
            print("-" * len(step.title))
            print(step.description)
            for note in step.notes:
                print(f"  - {note}")
            preview = step.preview()
            if preview["added"]:
                print("  Added:")
                for item in preview["added"]:
                    print(f"    {item}")
            if preview["removed"]:
                print("  Removed:")
                for item in preview["removed"]:
                    print(f"    {item}")
            print()

        print("Final grammar:")
        print(result.final.pretty())
        print()


def _run_single(grammar: Grammar, label: str, args: argparse.Namespace, export_dir: Path | None) -> int:
    result = CNFConverter().convert(grammar)
    _print_result(label, grammar, result, args.show_steps)

    if result.is_valid():
        print("Validation: CNF satisfied")
    else:
        print("Validation: CNF failed")
        for issue in result.issues:
            print(f"  - {issue}")

    if export_dir is not None:
        write_report_bundle(export_dir, label, grammar, result)
        print(f"Exported bundle to {export_dir}")

    if args.validate and not result.is_valid():
        return 1
    return 0


def main() -> int:
    args = _parse_args()

    if args.list_variants:
        print("Available variants:")
        for variant_id in list_variants():
            print(f"- Variant {variant_id}")
        return 0

    if args.grammar_file:
        grammar = _load_custom_grammar(args.grammar_file)
        label = Path(args.grammar_file).stem
        export_dir = Path(args.export_dir) if args.export_dir else None
        return _run_single(grammar, label, args, export_dir)

    if args.variant == "all":
        overall_exit = 0
        base_export_dir = Path(args.export_dir) if args.export_dir else None
        for variant_id in list_variants():
            grammar = load_variant_grammar(variant_id)
            label = f"Variant {variant_id}"
            export_dir = base_export_dir / f"variant_{variant_id}" if base_export_dir else None
            exit_code = _run_single(grammar, label, args, export_dir)
            overall_exit = max(overall_exit, exit_code)
        return overall_exit

    variant_id = int(args.variant)
    grammar = load_variant_grammar(variant_id)
    label = f"Variant {variant_id}"
    export_dir = Path(args.export_dir) if args.export_dir else None
    return _run_single(grammar, label, args, export_dir)


if __name__ == "__main__":
    raise SystemExit(main())