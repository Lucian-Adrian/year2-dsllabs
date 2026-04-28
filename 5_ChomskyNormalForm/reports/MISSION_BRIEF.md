# Mission Brief

This lab is the CNF version of the earlier overachieving projects: it is not just a normalizer, it is a grammar analysis and presentation tool.

## Mission Goals

- Convert the official Lab 5 grammars to Chomsky Normal Form.
- Accept arbitrary grammars in the same notation for the bonus condition.
- Expose each rewrite stage instead of hiding the algorithm behind a single output.
- Provide a Streamlit interface for demoing the result live.
- Export a report bundle with Mermaid visuals and machine-readable results.

## Strong Result

The repository now contains a reusable grammar converter, a catalog of the 32 official variants, and a UI that can show the original grammar, the rewrite trace, and the final CNF grammar side by side. The full catalog smoke test passes, and the default Variant 13 demo converts cleanly to CNF.

## Demo Commands

```powershell
streamlit run 5_ChomskyNormalForm/app.py
python 5_ChomskyNormalForm/main.py --variant 13 --show-steps --validate
python 5_ChomskyNormalForm/main.py --variant all --validate --export-dir 5_ChomskyNormalForm/reports/generated
```