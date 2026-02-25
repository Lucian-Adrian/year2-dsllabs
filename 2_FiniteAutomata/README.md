# Lab 2 — Determinism in Finite Automata

## Course: Formal Languages & Finite Automata | Variant: 13

---

## Overview

This lab builds an **Interactive State-Space Compiler** that converts a Non-Deterministic Finite Automaton (NDFA) into a Deterministic Finite Automaton (DFA) using the Powerset (Subset) Construction algorithm.

The project is structured into five modular layers that each solve one formal task:

| Layer | Module | Task |
|---|---|---|
| Config Router | `config/variant_13_ndfa.json` | Load any automaton from JSON |
| Chomsky Linter | `src/grammar.py` | Classify grammar by Chomsky hierarchy |
| State-Space Evaluator | `src/ndfa.py` | Detect non-determinism |
| Powerset Compiler | `src/powerset.py` | Convert NDFA → DFA |
| Reverse Engineer | `src/powerset.py` → `DFA.to_grammar()` | Extract grammar from DFA |

---

## Variant 13 — NDFA Definition

```
Q  = {q0, q1, q2, q3}
Σ  = {a, b}
F  = {q3}
δ(q0, a) = q0
δ(q0, b) = q1
δ(q1, a) = q1   ← non-deterministic
δ(q1, a) = q2   ← non-deterministic
δ(q1, b) = q3
δ(q2, a) = q2
δ(q2, b) = q3
```

The non-determinism is at state `q1` on input `a`: it can transition to both `q1` and `q2` simultaneously.

---

## Quick Start

```powershell
# 1. Navigate to the lab directory
cd 2_FiniteAutomata

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the CLI
python main.py --info
python main.py --classify
python main.py --compile --table
python main.py --compile --validate "bab"
python main.py --visualize-ndfa
python main.py --compile --visualize-dfa

# 4. Launch the interactive Streamlit dashboard
streamlit run app.py

# 5. Run tests
pytest tests/ -v
```

---

## Project Structure

```
2_FiniteAutomata/
|-- config/
|   `-- variant_13_ndfa.json    # NDFA definition for Variant 13
|-- src/
|   |-- __init__.py
|   |-- ndfa.py                 # NDFA class: load, determinism check, FA→grammar
|   |-- powerset.py             # Powerset construction + DFA class
|   |-- grammar.py              # Generic grammar + Chomsky hierarchy classifier
|   `-- visualizer.py           # PyVis interactive graph renderer
|-- tests/
|   `-- test_lab2.py            # ~40 tests across all 5 layers
|-- app.py                      # Streamlit interactive dashboard
|-- main.py                     # CLI
|-- requirements.txt
`-- README.md
```

---

## Tasks

### Task 2a — Chomsky Hierarchy Classification

`Grammar.classify_chomsky()` in `src/grammar.py` analyses each production rule algebraically:

- **Type 3 (Regular)**: LHS is a single non-terminal; RHS is `ε`, a single terminal, or `terminal non-terminal` (right-linear) or `non-terminal terminal` (left-linear). All productions must share the same linearity direction.
- **Type 2 (Context-Free)**: LHS is a single non-terminal; RHS is unrestricted.
- **Type 1 (Context-Sensitive)**: `|LHS| ≤ |RHS|` for all productions (S→ε excepted).
- **Type 0 (Unrestricted)**: Anything else.

The grammar extracted from Variant 13's NDFA classifies as **Type 3 — Regular Grammar** (right-linear).

### Task 3a — FA to Regular Grammar

`NDFA.to_grammar()` in `src/ndfa.py` extracts right-linear productions:

- For each transition `δ(qi, c) = qj` where `qj ∈ F`: produces `qi → c`
- For each transition `δ(qi, c) = qj`: produces `qi → c qj`
- For each accepting state `qi ∈ F`: produces `qi → ε`

### Task 3b — Determinism Check

`NDFA.is_deterministic()` returns `False` if any `(state, symbol)` pair maps to more than one target state. `non_deterministic_sources()` returns the exact conflict pairs for diagnostic display.

For Variant 13: `δ(q1, a) = {q1, q2}` → conflict at `(q1, a)`.

### Task 3c — NDFA to DFA (Powerset Construction)

`powerset_construction(ndfa)` in `src/powerset.py` implements the BFS-based subset construction:

1. Start state: `{q0}` (the frozenset containing only the NDFA start state)
2. For each unvisited macro-state and each symbol, compute the union of all reachable NDFA states
3. Each new frozenset becomes a new DFA state
4. Any macro-state containing an NDFA accepting state becomes a DFA accepting state

Result for Variant 13:

| Macro-state | on a | on b | Accepting? |
|---|---|---|---|
| `{q0}` | `{q0}` | `{q1}` | |
| `{q1}` | `{q1,q2}` | `{q3}` | |
| `{q1,q2}` | `{q1,q2}` | `{q3}` | |
| `{q3}` | `∅` | `∅` | ✔ |
| `∅` | `∅` | `∅` | |

---

## The Language

The NDFA (and its equivalent DFA) accept strings of the form **`a* b a* b`**: zero or more `a`'s, then `b`, then zero or more `a`'s, then `b`. No other strings are accepted.

Examples:
- Accepted: `bb`, `abb`, `bab`, `baab`, `aabb`, `abab`
- Rejected: `b`, `a`, `ba`, `bbb`, `ababab`

---

## Interactive Dashboard

Run `streamlit run app.py` to open the dashboard in your browser.

Features:
1. Upload any NDFA JSON or use the default Variant 13
2. Instant non-determinism diagnostic with conflict highlighting
3. Interactive physics-based NDFA graph (drag nodes to explore)
4. Chomsky hierarchy classification with proof evidence
5. Single-click powerset compilation to DFA
6. Side-by-side NDFA/DFA comparison
7. Step-by-step powerset construction table
8. Live string inference tester with state-by-state highlighting

---

## References

- Hopcroft, J. E., Motwani, R., & Ullman, J. D. (2006). *Introduction to Automata Theory, Languages, and Computation*. Pearson.
- PyVis Documentation: https://pyvis.readthedocs.io/
- Streamlit Documentation: https://docs.streamlit.io/
- Pytest Framework: https://pytest.org/
- Source code (GitHub): https://github.com/Lucian-Adrian/year2-dsllabs/tree/master/2_FiniteAutomata
