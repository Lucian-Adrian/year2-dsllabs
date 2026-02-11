import argparse

from src.grammar import Grammar
from src.visualizer import plot_automaton


def main():
    parser = argparse.ArgumentParser(
        description="Regular Grammar to Finite Automaton Tool"
    )
    parser.add_argument(
        "--config", default="config/variant_13.json", help="Path to config JSON"
    )
    parser.add_argument("--generate", type=int, help="Generate N strings")
    parser.add_argument("--validate", help="Validate a string")
    parser.add_argument("--visualize", action="store_true", help="Show automaton graph")
    parser.add_argument(
        "--benchmark", type=int, help="Benchmark generation speed (N samples)"
    )

    args = parser.parse_args()

    grammar = Grammar(args.config)
    automaton = grammar.build_finite_automaton()

    if args.generate:
        print(f"Generating {args.generate} strings:")
        for _ in range(args.generate):
            sample = grammar.sample()
            accepted = automaton.check(sample)
            print(f"  {sample} -> {'Accepted' if accepted else 'Rejected'}")

    if args.validate:
        accepted, path = automaton.check_with_path(args.validate)
        print(f"String '{args.validate}' -> {'Accepted' if accepted else 'Rejected'}")
        print(f"Path: {path}")

    if args.visualize:
        plot_automaton(automaton, title="Finite Automaton")

    if args.benchmark:
        import time

        start = time.time()
        for _ in range(args.benchmark):
            grammar.sample()
        elapsed = time.time() - start
        print(
            f"Generated {args.benchmark} strings in {elapsed:.2f}s ({args.benchmark / elapsed:.1f} per second)"
        )


if __name__ == "__main__":
    main()
