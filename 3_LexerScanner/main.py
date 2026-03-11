from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from src.highlighter import highlight_source
from src.lexer import LexerConfig, LexicalError, TensorScriptLexer
from src.tokens import Token, TokenType

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_DEMO_FILE = PROJECT_ROOT / "examples" / "tensorscript_demo.tscript"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TensorScript Sigmoid Engine v3")
    parser.add_argument("--file", help="Path to a TensorScript source file")
    parser.add_argument("--code", help="Inline TensorScript source code")
    parser.add_argument(
        "--demo", action="store_true", help="Use the bundled TensorScript demo"
    )
    parser.add_argument(
        "--no-comments", action="store_true", help="Do not emit comment tokens"
    )
    parser.add_argument(
        "--no-highlight",
        action="store_true",
        help="Skip syntax-highlighted source output",
    )
    parser.add_argument(
        "--json", action="store_true", help="Print token stream as JSON"
    )
    parser.add_argument(
        "--stats", action="store_true", help="Print token frequency statistics"
    )
    return parser.parse_args()


def load_source(args: argparse.Namespace) -> tuple[str, str]:
    if args.code:
        return args.code, "<cli>"
    if args.file:
        path = Path(args.file)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        return path.read_text(encoding="utf-8"), str(path)
    return DEFAULT_DEMO_FILE.read_text(encoding="utf-8"), str(DEFAULT_DEMO_FILE)


def build_token_table(tokens: list[Token]) -> Table:
    table = Table(
        title="TensorScript Token DataFrame",
        box=box.MINIMAL_DOUBLE_HEAD,
        show_lines=True,
        header_style="bold white on dark_blue",
        row_styles=["", "dim"],
        expand=True,
    )
    table.add_column("Line", justify="right", style="cyan", no_wrap=True)
    table.add_column("Column", justify="right", style="cyan", no_wrap=True)
    table.add_column("Token Type", style="magenta")
    table.add_column("Lexeme", style="green")
    table.add_column("Memory Address", style="yellow")

    for token in tokens:
        table.add_row(*token.to_row())
    return table


def build_stats_table(tokens: list[Token]) -> Table:
    counter = Counter(token.token_type.label for token in tokens)
    table = Table(
        title="Token Distribution",
        box=box.SIMPLE_HEAVY,
        header_style="bold white on dark_green",
    )
    table.add_column("Token Type", style="cyan")
    table.add_column("Count", justify="right", style="green")
    for token_type, count in sorted(counter.items()):
        table.add_row(token_type, str(count))
    return table


def build_summary_panel(
    source_text: str, source_name: str, tokens: list[Token]
) -> Panel:
    identifier_count = sum(
        1 for token in tokens if token.token_type is TokenType.IDENTIFIER
    )
    float_count = sum(1 for token in tokens if token.token_type is TokenType.FLOAT)
    function_count = sum(
        1 for token in tokens if token.token_type is TokenType.MATH_FUNCTION
    )
    message = (
        f"Source: {source_name}\n"
        f"Characters: {len(source_text)}\n"
        f"Lines: {len(source_text.splitlines())}\n"
        f"Tokens streamed: {len(tokens)}\n"
        f"Identifiers: {identifier_count}\n"
        f"Float literals: {float_count}\n"
        f"Math functions: {function_count}"
    )
    return Panel(message, title="Lexer Summary", border_style="bright_blue")


def print_json(console: Console, tokens: list[Token]) -> None:
    payload = [token.to_dict() for token in tokens]
    console.print_json(json.dumps(payload, indent=2))


def main() -> int:
    args = parse_args()
    console = Console()
    source_text, source_name = load_source(args)

    lexer = TensorScriptLexer(
        source_text,
        source_name=source_name,
        config=LexerConfig(emit_comments=not args.no_comments),
    )

    try:
        tokens = lexer.collect()
    except LexicalError as error:
        console.print(
            Panel(
                error.render(), title="Sigmoid Engine v3 Diagnostic", border_style="red"
            )
        )
        return 1

    console.print(build_summary_panel(source_text, source_name, tokens))
    console.print(build_token_table(tokens))

    if args.stats:
        console.print(build_stats_table(tokens))

    if args.json:
        print_json(console, tokens)

    if not args.no_highlight:
        console.print(
            Panel(
                highlight_source(source_text, tokens),
                title="ANSI Syntax Highlight",
                border_style="yellow",
            )
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
