# Laboratory Work 4 - Executive Summary

## Topic

Dynamic regular-expression interpretation and bounded generation for all assignment variants.

## What Was Built

This laboratory work implements a universal regex engine for the Lab 4 assignment. Instead of hardcoding one variant, the system:

- normalizes handwritten-style regex notation,
- parses expressions with a recursive-descent parser,
- converts them into an abstract syntax tree,
- generates valid words deterministically or through random traced sampling,
- validates generated outputs with an independent Python regex backend,
- and exports explainability artifacts such as AST and trace diagrams.

## Why This Matters

The assignment explicitly asks for dynamic interpretation of regular expressions. The important achievement here is therefore not just producing valid outputs, but building a reusable symbolic processing pipeline that works across all four variants and all twelve expressions.

## Main Technical Ideas

- `src/parser.py`: normalization + recursive-descent parsing
- `src/ast_nodes.py`: typed AST representation
- `src/generator.py`: bounded language generation, random sampling, and regex emission
- `src/visualization.py`: Mermaid diagrams and structural metrics
- `src/variants.py`: universal all-variant source definitions
- `tests/test_lab4_regex.py`: verification of parsing, examples, generation, validation, and visuals

## Deliverables Added in This Submission Package

- `reports/report.tex`: full academic report with correctness, benchmarking, reproducibility, and appendices
- `reports/report.pdf`: compiled 52-page PDF artifact
- `presentation/slides.md`: 36-slide Slidev deck for live presenting
- `presentation/PRESENTATION_SCRIPT.md`: speaker-ready script
- `reports/evidence/summary.json`: machine-readable all-variant analysis bundle
- `reports/evidence/summary.md`: human-readable analytical summary
- `reports/evidence/terminal_transcript.txt`: real terminal-style evidence transcript

## Recommended Commands

```powershell
python 4_regular_expressions/main.py --variant all --samples 8 --validate
python 4_regular_expressions/main.py --variant 4 --samples 10 --show-steps --validate
python 4_regular_expressions/main.py --variant all --samples 6 --show-steps --export-mermaid-dir 4_regular_expressions/reports/visuals
python 4_regular_expressions/main.py --variant all --samples 4 --max-results 12 --validate --export-analysis-dir 4_regular_expressions/reports/evidence --benchmark-iterations 5
python -m pytest 4_regular_expressions/tests -q
```

## Notes

The long-form analysis, theoretical framing, variant comparison, and full code appendices are contained in `report.tex`. This Markdown file is intentionally kept short as a companion summary.
