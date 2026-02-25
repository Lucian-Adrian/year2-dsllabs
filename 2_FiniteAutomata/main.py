"""
Command-line interface for Lab 2 — NDFA / DFA Toolkit.

Usage examples
--------------
  python main.py --info
  python main.py --classify
  python main.py --compile
  python main.py --validate "abab"
  python main.py --compile --validate "abab"
  python main.py --visualize-ndfa
  python main.py --compile --visualize-dfa
"""

import argparse
import sys

from src.grammar import Grammar
from src.ndfa import NDFA
from src.powerset import powerset_construction
from src.visualizer import ndfa_to_html, dfa_to_html


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_ndfa(path: str) -> NDFA:
    try:
        return NDFA.from_json(path)
    except FileNotFoundError:
        print(f"[ERROR] Config file not found: {path}")
        sys.exit(1)


def build_grammar_from_ndfa(ndfa: NDFA) -> Grammar:
    """Wrap the FA-derived productions into a Grammar for Chomsky classification."""
    productions = ndfa.to_grammar()
    non_terminals = set(ndfa.states)
    terminals = set(ndfa.alphabet)
    return Grammar.from_fa_productions(non_terminals, terminals, ndfa.start, productions)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Lab 2 — NDFA/DFA State-Space Compiler"
    )
    parser.add_argument(
        "--config",
        default="config/variant_13_ndfa.json",
        help="Path to NDFA JSON config",
    )
    parser.add_argument("--info", action="store_true", help="Show raw NDFA info")
    parser.add_argument(
        "--classify",
        action="store_true",
        help="Classify grammar derived from the NDFA (Chomsky hierarchy)",
    )
    parser.add_argument(
        "--compile",
        action="store_true",
        help="Run powerset construction to convert NDFA → DFA",
    )
    parser.add_argument(
        "--validate",
        metavar="STRING",
        help="Validate a string against the compiled DFA",
    )
    parser.add_argument(
        "--visualize-ndfa",
        action="store_true",
        help="Save NDFA interactive graph as ndfa.html",
    )
    parser.add_argument(
        "--visualize-dfa",
        action="store_true",
        help="Save DFA interactive graph as dfa.html (requires --compile)",
    )
    parser.add_argument(
        "--table",
        action="store_true",
        help="Print the powerset construction table (requires --compile)",
    )

    args = parser.parse_args()

    # ---- Load NDFA
    ndfa = load_ndfa(args.config)

    # ---- --info
    if args.info or not any(
        [args.classify, args.compile, args.validate, args.visualize_ndfa, args.visualize_dfa]
    ):
        print("=" * 60)
        print("NDFA DEFINITION")
        print("=" * 60)
        print(f"  States    : {ndfa.states}")
        print(f"  Alphabet  : {ndfa.alphabet}")
        print(f"  Start     : {ndfa.start}")
        print(f"  Accepting : {sorted(ndfa.accepting)}")
        print()
        print("Transitions:")
        for (state, sym), targets in sorted(ndfa.transitions.items()):
            print(f"  δ({state}, {sym}) = {{{', '.join(sorted(targets))}}}")
        print()
        det = ndfa.is_deterministic()
        if det:
            print("✔  This automaton IS deterministic (DFA).")
        else:
            conflicts = ndfa.non_deterministic_sources()
            print("✘  This automaton is NOT deterministic (NDFA).")
            print("   Conflict pairs (state, symbol):")
            for state, sym in conflicts:
                print(f"     δ({state}, {sym}) → {sorted(ndfa.transitions[(state, sym)])}")

    # ---- --classify
    if args.classify:
        print()
        print("=" * 60)
        print("CHOMSKY HIERARCHY CLASSIFICATION")
        print("=" * 60)
        grammar = build_grammar_from_ndfa(ndfa)
        print(grammar)
        print()
        type_num, label, evidence = grammar.classify_chomsky()
        print(f"Classification: {label}")
        print()
        print("Evidence:")
        for line in evidence:
            print(f"  {line}")

    # ---- --compile
    dfa = None
    if args.compile or args.validate or args.visualize_dfa or args.table:
        print()
        print("=" * 60)
        print("POWERSET CONSTRUCTION  (NDFA → DFA)")
        print("=" * 60)
        dfa = powerset_construction(ndfa)
        print(f"  DFA states    : {dfa.states}")
        print(f"  DFA accepting : {sorted(dfa.accepting)}")
        print(f"  DFA start     : {dfa.start}")
        print()
        print("DFA Transitions:")
        for (state, sym), tgt in sorted(dfa.transitions.items()):
            print(f"  δ({state}, {sym}) = {tgt}")

        if args.table:
            print()
            print("Powerset Construction Table:")
            # Header
            header = ["Macro-state"] + dfa.alphabet
            col_widths = [max(len(h), max((len(s["macro_state"]) for s in dfa.construction_steps), default=0) + 2) for h in header]
            col_widths[0] = max(col_widths[0], 20)
            header_str = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(header))
            print("  " + header_str)
            print("  " + "-" * len(header_str))
            for step in dfa.construction_steps:
                row = [step["macro_state"]] + [step["transitions"].get(sym, "—") for sym in dfa.alphabet]
                print("  " + " | ".join(c.ljust(col_widths[i]) for i, c in enumerate(row)))

    # ---- --validate
    if args.validate is not None:
        if dfa is None:
            dfa = powerset_construction(ndfa)
        s = args.validate
        accepted, path = dfa.trace(s)
        result = "ACCEPTED ✔" if accepted else "REJECTED ✘"
        print()
        print(f"String {s!r}  →  {result}")
        print(f"State path: {' → '.join(path)}")

    # ---- --visualize-ndfa
    if args.visualize_ndfa:
        html = ndfa_to_html(ndfa)
        with open("ndfa.html", "w", encoding="utf-8") as fh:
            fh.write(html)
        print()
        print("NDFA graph saved to ndfa.html — open in a browser.")

    # ---- --visualize-dfa
    if args.visualize_dfa:
        if dfa is None:
            dfa = powerset_construction(ndfa)
        html = dfa_to_html(dfa)
        with open("dfa.html", "w", encoding="utf-8") as fh:
            fh.write(html)
        print()
        print("DFA graph saved to dfa.html — open in a browser.")


if __name__ == "__main__":
    main()
