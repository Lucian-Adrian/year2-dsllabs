"""
Streamlit Dashboard — Interactive State-Space Compiler
"Resolving Computational Uncertainty: From NDFA to DFA"

Run with:
    cd 2_FiniteAutomata
    streamlit run app.py
"""

import json
from collections import defaultdict
from typing import Dict

import streamlit as st
import streamlit.components.v1 as components

from src.grammar import Grammar
from src.ndfa import NDFA
from src.powerset import DFA, powerset_construction
from src.visualizer import dfa_to_html, ndfa_to_html

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="State-Space Compiler",
    page_icon="⚛",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS — dark theme, glowing effects
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Dark base */
    .stApp { background-color: #0d0d1a; color: #e0e0ff; }
    section[data-testid="stSidebar"] { background-color: #12122a; }

    /* Headers */
    h1 { color: #7eb8ff; font-family: 'Courier New', monospace; letter-spacing: 2px; }
    h2, h3 { color: #a0c8ff; }

    /* Diagnostic banners */
    .diag-danger {
        background: #3a0000; border: 1px solid #ff4444; border-radius: 6px;
        padding: 12px 18px; color: #ff8888; font-family: monospace; font-size: 14px;
    }
    .diag-ok {
        background: #003a00; border: 1px solid #44ff44; border-radius: 6px;
        padding: 12px 18px; color: #88ff88; font-family: monospace; font-size: 14px;
    }
    .diag-info {
        background: #00103a; border: 1px solid #4488ff; border-radius: 6px;
        padding: 12px 18px; color: #88aaff; font-family: monospace; font-size: 14px;
    }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: #1a1a3a; border-radius: 8px; padding: 10px;
    }

    /* Code blocks */
    code { background: #1a1a2e; color: #a0c4ff; }

    /* Button */
    .stButton > button {
        background: linear-gradient(135deg, #1a1a5e, #3a3aaa);
        color: white; border: 1px solid #5555cc;
        font-size: 16px; padding: 12px 30px; border-radius: 8px;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #3a3aaa, #6666dd);
        box-shadow: 0 0 15px #5555cc;
    }

    /* Text input */
    .stTextInput input {
        background: #1a1a2e; color: #e0e0ff; border: 1px solid #4444aa;
        font-family: 'Courier New', monospace; font-size: 18px;
    }

    /* Step indicator */
    .step-active { background: #2a2a6a; border-radius: 4px; padding: 4px 8px; color: #ffd700; }
    .step-visited { color: #88aa88; }
    .step-pending { color: #555; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar — Configuration
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚙ Configuration")

    upload = st.file_uploader(
        "Upload automaton JSON",
        type=["json"],
        help="Must follow the config/variant_13_ndfa.json schema.",
    )

    use_default = st.checkbox("Use Variant 13 (default)", value=upload is None)

    st.markdown("---")
    st.markdown("### Options")
    include_dead = st.checkbox("Include dead state ∅ in DFA", value=True)
    show_grammar = st.checkbox("Show extracted grammar", value=True)
    show_table = st.checkbox("Show powerset construction table", value=True)

    st.markdown("---")
    st.markdown(
        """
        **State-Space Compiler**
        Lab 2 · Formal Languages & FA
        Variant 13
        """
    )


# ---------------------------------------------------------------------------
# Load NDFA
# ---------------------------------------------------------------------------
@st.cache_data
def load_ndfa_from_bytes(data: bytes) -> NDFA:
    obj = json.loads(data)
    raw: Dict = defaultdict(set)
    for t in obj["transitions"]:
        raw[(t["from"], t["on"])].add(t["to"])
    return NDFA(
        states=obj["states"],
        alphabet=obj["alphabet"],
        transitions=dict(raw),
        start=obj["start"],
        accepting=obj["accepting"],
    )


@st.cache_data
def load_default_ndfa() -> NDFA:
    return NDFA.from_json("config/variant_13_ndfa.json")


if upload is not None:
    ndfa = load_ndfa_from_bytes(upload.read())
elif use_default:
    ndfa = load_default_ndfa()
else:
    st.info("Upload an automaton JSON file or enable 'Use Variant 13'.")
    st.stop()


# ---------------------------------------------------------------------------
# Title
# ---------------------------------------------------------------------------
st.markdown(
    "<h1>⚛ State-Space Compiler</h1>"
    "<p style='color:#7070aa; font-family:monospace;'>"
    "Resolving Computational Uncertainty: NDFA → DFA</p>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Section 1 — Diagnosis
# ---------------------------------------------------------------------------
st.markdown("## 1. Diagnostic Scanner")

det = ndfa.is_deterministic()
conflicts = ndfa.non_deterministic_sources()

diag_col1, diag_col2, diag_col3 = st.columns(3)
with diag_col1:
    st.metric("States", len(ndfa.states))
with diag_col2:
    st.metric("Alphabet symbols", len(ndfa.alphabet))
with diag_col3:
    st.metric("Transition rules", sum(len(v) for v in ndfa.transitions.values()))

if det:
    st.markdown(
        '<div class="diag-ok">✔  DIAGNOSTIC: Already Deterministic (DFA). No compilation needed.</div>',
        unsafe_allow_html=True,
    )
else:
    conflict_str = "  |  ".join(f"δ({s},{sym})→{sorted(ndfa.transitions[(s,sym)])}" for s,sym in conflicts)
    st.markdown(
        f'<div class="diag-danger">'
        f'✘  DIAGNOSTIC: Non-Deterministic FA detected!  Uncertainty found at:  {conflict_str}'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown("")

# Transition table
with st.expander("Transition Table (NDFA)", expanded=False):
    rows = []
    for (state, sym), targets in sorted(ndfa.transitions.items()):
        rows.append({
            "From": state,
            "On": sym,
            "To": "{" + ", ".join(sorted(targets)) + "}",
            "Non-det?": "⚠ YES" if len(targets) > 1 else "",
        })
    st.table(rows)

# ---------------------------------------------------------------------------
# Section 2 — NDFA Graph
# ---------------------------------------------------------------------------
st.markdown("## 2. NDFA Graph — Quantum State Space")
st.markdown(
    "_Drag nodes to explore the non-deterministic structure. "
    "Red/orange nodes are conflict points._"
)

ndfa_html = ndfa_to_html(ndfa, highlight_conflicts=True)
components.html(ndfa_html, height=500, scrolling=False)

# ---------------------------------------------------------------------------
# Section 3 — Chomsky Classification
# ---------------------------------------------------------------------------
st.markdown("## 3. Chomsky Hierarchy Linter")

grammar_prods = ndfa.to_grammar()
grammar = Grammar.from_fa_productions(
    non_terminals=set(ndfa.states),
    terminals=set(ndfa.alphabet),
    start=ndfa.start,
    productions=grammar_prods,
)
type_num, type_label, evidence = grammar.classify_chomsky()

st.markdown(
    f'<div class="diag-info">'
    f'📐  Grammar extracted from NDFA classifies as: <b>{type_label}</b>'
    f'</div>',
    unsafe_allow_html=True,
)

if show_grammar:
    with st.expander("Extracted Grammar Productions", expanded=False):
        for lhs, rhs in grammar_prods:
            st.markdown(f"- `{lhs}` → `{rhs if rhs else 'ε'}`")

    with st.expander("Chomsky Evidence (proof)", expanded=False):
        for line in evidence:
            st.markdown(f"- {line}")

# ---------------------------------------------------------------------------
# Section 4 — Powerset Compiler
# ---------------------------------------------------------------------------
st.markdown("## 4. Powerset Compiler  —  Collapse State Space")
st.markdown(
    "_Click the button to run the Subset Construction algorithm and "
    "collapse the NDFA's parallel timelines into a single deterministic machine._"
)

if "dfa" not in st.session_state:
    st.session_state["dfa"] = None

compile_col, _ = st.columns([1, 3])
with compile_col:
    compile_btn = st.button("⚡ Collapse State Space (Compile to DFA)", use_container_width=True)

if compile_btn:
    with st.spinner("Running powerset construction..."):
        st.session_state["dfa"] = powerset_construction(ndfa, include_dead=include_dead)

dfa: DFA | None = st.session_state["dfa"]

if dfa is not None:
    st.markdown(
        '<div class="diag-ok">'
        '✔  OPTIMISATION COMPLETE: Deterministic FA generated.  '
        f'States: {len(dfa.states)}  |  Inference time: O(n)'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown("")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("DFA States", len(dfa.states))
    with m2:
        st.metric("DFA Accepting", len(dfa.accepting))
    with m3:
        st.metric("DFA Transitions", len(dfa.transitions))
    with m4:
        ndfa_states = 2 ** len(ndfa.states)
        st.metric("Worst-case states", f"2^{len(ndfa.states)}={ndfa_states}", delta=f"-{ndfa_states - len(dfa.states)} pruned")

    # ---- DFA Graph (side-by-side with NDFA)
    st.markdown("### Side-by-Side Comparison")
    left_g, right_g = st.columns(2)
    with left_g:
        st.markdown("**NDFA** (uncertain)")
        components.html(ndfa_html, height=460, scrolling=False)
    with right_g:
        st.markdown("**DFA** (deterministic)")
        dfa_html_base = dfa_to_html(dfa)
        components.html(dfa_html_base, height=460, scrolling=False)

    # ---- Powerset construction table
    if show_table:
        with st.expander("Powerset Construction Table (step-by-step proof)", expanded=True):
            header_cols = ["Macro-state"] + dfa.alphabet + ["Accepting?"]
            steps = dfa.construction_steps  # type: ignore[attr-defined]
            table_data = []
            for step in steps:
                row = {
                    "Macro-state": step["macro_state"],
                }
                for sym in dfa.alphabet:
                    row[sym] = step["transitions"].get(sym, "—")
                row["Accepting?"] = "✔" if step["macro_state"] in dfa.accepting else ""
                table_data.append(row)
            st.table(table_data)

    # ---- DFA Transition Table
    with st.expander("DFA Transition Table", expanded=False):
        dfa_rows = []
        for (state, sym), tgt in sorted(dfa.transitions.items()):
            dfa_rows.append({
                "From": state,
                "On": sym,
                "To": tgt,
            })
        st.table(dfa_rows)

    # ---- Chomsky from DFA
    st.markdown("### Grammar Extracted from DFA")
    dfa_prods = dfa.to_grammar()
    dfa_grammar = Grammar.from_fa_productions(
        non_terminals=set(dfa.states),
        terminals=set(dfa.alphabet),
        start=dfa.start,
        productions=dfa_prods,
    )
    dfa_type_num, dfa_type_label, _ = dfa_grammar.classify_chomsky()
    st.markdown(
        f'<div class="diag-info">'
        f'📐  DFA grammar classifies as: <b>{dfa_type_label}</b> — '
        f'information preserved across compilation. ✔'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ====================================================================
    # Section 5 — Live Inference Tester
    # ====================================================================
    st.markdown("---")
    st.markdown("## 5. Live Inference Tester")
    st.markdown(
        "_Type a string to trace it through the DFA. "
        "Use the step slider to see which state is active at each character._"
    )

    test_col, step_col = st.columns([2, 1])
    with test_col:
        test_string = st.text_input(
            "Input string",
            value="",
            placeholder="e.g. abab",
            label_visibility="collapsed",
        )
    with step_col:
        if test_string:
            step = st.slider(
                "Step",
                min_value=0,
                max_value=len(test_string),
                value=len(test_string),
                step=1,
            )
        else:
            step = 0

    if test_string:
        accepted, full_path = dfa.trace(test_string)

        # Show the path with step highlighting
        path_html = []
        for i, state in enumerate(full_path):
            char = test_string[i - 1] if i > 0 else "→"
            if i == step:
                path_html.append(f'<span class="step-active">{state}</span>')
            elif i < step:
                path_html.append(f'<span class="step-visited">{state}</span>')
            else:
                path_html.append(f'<span class="step-pending">{state}</span>')
            if i < len(full_path) - 1:
                sym = test_string[i] if i < len(test_string) else ""
                path_html.append(f' <span style="color:#666">—[{sym}]→</span> ')

        st.markdown(
            "<p style='font-family:monospace; font-size:16px; line-height:2.2'>"
            + "".join(path_html)
            + "</p>",
            unsafe_allow_html=True,
        )

        # Active state at current step
        active = full_path[step] if step < len(full_path) else full_path[-1]
        trace_so_far = full_path[: step + 1]

        # Re-render DFA with highlighted active state
        highlighted_html = dfa_to_html(
            dfa, active_state=active, trace_path=trace_so_far
        )
        components.html(highlighted_html, height=480, scrolling=False)

        # Final verdict
        if step == len(test_string):
            if accepted:
                st.markdown(
                    f'<div class="diag-ok" style="font-size:22px; text-align:center;">'
                    f'✔  String <b>{test_string!r}</b> is ACCEPTED  →  Final state: {full_path[-1]}'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            else:
                dead_reason = ""
                if full_path[-1] == dfa.DEAD_LABEL:
                    dead_reason = " (no transition — dead state reached)"
                st.markdown(
                    f'<div class="diag-danger" style="font-size:22px; text-align:center;">'
                    f'✘  String <b>{test_string!r}</b> is REJECTED'
                    f'{dead_reason}  →  Final state: {full_path[-1]}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

else:
    st.markdown(
        '<div class="diag-info">👆  Click "Collapse State Space" above to compile the NDFA into a DFA.</div>',
        unsafe_allow_html=True,
    )
