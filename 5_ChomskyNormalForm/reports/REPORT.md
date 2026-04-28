# Laboratory Work 5 - Executive Summary

## Topic

Chomsky Normal Form conversion for the official Lab 5 grammar variants, with a generic grammar pipeline and an interactive visualization layer.

## What Was Built

This laboratory work implements a full grammar-normalization pipeline that rewrites a context-free grammar into Chomsky Normal Form while preserving the language. The pipeline is intentionally more capable than the minimum assignment: it can load the 32 official variants from the assignment PDF, accept custom grammars, explain every transformation step, and export a report bundle for presentation or grading.

## Why This Matters

Chomsky Normal Form is the cleanest syntax for many proofs and parser constructions. A good implementation has to do more than mechanically rewrite rules; it has to remove epsilon productions, eliminate renaming chains, prune useless symbols, isolate terminals, and binarize long productions without losing the grammar semantics. The lab is useful because it packages those theoretical steps into a reusable tool instead of a one-off solution.

## Main Technical Ideas

The code is split into a small number of focused modules:

- `src/grammar.py` defines the immutable grammar model and parsing helpers.
- `src/cnf.py` performs the normalization pipeline and records the trace.
- `src/catalog.py` loads the official variant catalog from `config/variants.json`.
- `src/visualization.py` builds Mermaid pipeline views and tabular summaries.
- `src/reporting.py` assembles a Markdown report bundle with visuals and JSON.
- `main.py` provides a CLI for batch conversion.
- `app.py` provides a Streamlit dashboard for interactive inspection.

## Transformation Pipeline

The converter applies the standard CNF rewrite sequence:

1. Add a fresh start symbol.
2. Eliminate epsilon productions.
3. Eliminate unit productions.
4. Remove non-productive and inaccessible symbols.
5. Replace terminals inside longer productions with pre-terminal symbols.
6. Binarize all productions longer than two symbols.
7. Run a final cleanup pass and validate the result.

This structure is stable, testable, and easy to explain during presentation.

## Validation

The test suite checks the full catalog loader, a representative official variant, epsilon and unit handling, binarization, and the report export path. That makes the final submission stronger than a single demo because it can be verified automatically and manually.

The CLI smoke test also ran successfully across every official variant in the catalog. Variant 13, which is used as the default demo, converts to CNF with 23 productions and 8 helper symbols in the current implementation.

## Conclusion

The final deliverable is a generic CNF converter with a polished interface and a strong report trail. It is designed to impress because it solves the assignment directly, covers the bonus case, and adds a presentation layer on top of the core algorithm.

## References

- Chomsky Normal Form: https://en.wikipedia.org/wiki/Chomsky_normal_form
- Streamlit documentation: https://docs.streamlit.io/