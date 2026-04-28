# Lab 5 - Chomsky Normal Form

## What This Lab Does

This lab converts context-free grammars into Chomsky Normal Form with a full transformation trace. It is deliberately overbuilt in the same spirit as the earlier labs:

- It supports the official 32 variants from `variants.pdf`.
- It accepts custom grammars from plain text or JSON.
- It shows every rewrite pass, not just the final answer.
- It exports a Markdown report bundle and Mermaid visuals.
- It includes a Streamlit dashboard for interactive inspection.
- The dashboard has a manual stepper that walks through each rewrite pass with explanations and a highlighted pipeline.

## Main Entry Points

From the repository root:

```powershell
pip install -r 5_ChomskyNormalForm/requirements.txt
streamlit run 5_ChomskyNormalForm/app.py
python 5_ChomskyNormalForm/main.py --variant 13 --show-steps --validate
python 5_ChomskyNormalForm/main.py --variant all --validate --export-dir 5_ChomskyNormalForm/reports/generated
python 5_ChomskyNormalForm/main.py --grammar-file 5_ChomskyNormalForm/examples/variant_13.txt --show-steps
```

## Architecture

- `src/grammar.py` holds the immutable grammar model and parser.
- `src/cnf.py` implements the transformation pipeline.
- `src/catalog.py` loads the official variant catalog.
- `src/visualization.py` builds Mermaid and table-friendly views.
- `src/reporting.py` writes the report bundle.
- `app.py` is the interactive Streamlit dashboard.
- `app.py` includes the manual step navigator and the active pipeline highlight.
- `main.py` is the CLI runner for automation and testing.

## Overachiever Goal

The project is not limited to a single hand-crafted grammar. The converter works on any grammar that follows the lab notation, and the app exposes the whole official catalog so the final submission can be demonstrated, compared, and verified variant by variant.

The Streamlit dashboard uses a plain-text source grammar render path, which keeps it portable even in environments where `pyarrow` or `pandas` binary wheels are unavailable.