"""
Streamlit Dashboard — State-Space Compiler
Lab 2 · Formal Languages & Finite Automata

Run:
    cd 2_FiniteAutomata && streamlit run app.py
"""

import json
import os
from collections import defaultdict
from typing import Dict, List, Optional

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
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Design system — clean dark theme
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    html { color-scheme: dark; }
    *, *::before, *::after { box-sizing: border-box; }

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

    .stApp {
        background-color: #0a0a0a;
        color: #ededed;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 0.9375rem;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #111111;
        border-right: 1px solid #1f1f1f;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] label { color: #888 !important; font-size: 0.8rem !important; }
    section[data-testid="stSidebar"] h2 {
        color: #ededed !important; font-size: 0.8rem !important;
        font-weight: 600 !important; letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
    }

    /* Typography */
    h1 {
        color: #ffffff !important; font-size: 1.35rem !important;
        font-weight: 600 !important; letter-spacing: -0.03em !important;
        line-height: 1.3 !important; text-wrap: balance;
    }
    h2 {
        color: #444 !important; font-size: 0.72rem !important;
        font-weight: 600 !important; text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        margin-top: 2.2rem !important; margin-bottom: 0.75rem !important;
    }
    h3 {
        color: #ededed !important; font-size: 0.9rem !important;
        font-weight: 600 !important; letter-spacing: -0.01em !important;
    }
    p { color: #666; line-height: 1.6; font-size: 0.875rem; }
    hr { border: none; border-top: 1px solid #1a1a1a; margin: 2rem 0; }

    /* Banners */
    .banner {
        padding: 9px 13px; border-radius: 6px;
        font-size: 0.8rem; font-family: 'JetBrains Mono', monospace;
        line-height: 1.5; margin: 0.5rem 0;
    }
    .banner-error  { background: #0f0505; border: 1px solid #3b0f0f; color: #fca5a5; }
    .banner-ok     { background: #050f05; border: 1px solid #0f3b0f; color: #86efac; }
    .banner-info   { background: #05080f; border: 1px solid #0f1e3b; color: #93c5fd; }
    .banner strong { font-weight: 600; }

    /* Metrics */
    [data-testid="metric-container"] {
        background: #111111; border: 1px solid #1f1f1f;
        border-radius: 6px; padding: 12px 16px;
    }
    [data-testid="stMetricValue"] {
        color: #ffffff !important; font-size: 1.5rem !important;
        font-weight: 600 !important; font-variant-numeric: tabular-nums;
    }
    [data-testid="stMetricLabel"] {
        color: #555 !important; font-size: 0.72rem !important;
        text-transform: uppercase; letter-spacing: 0.05em;
    }
    [data-testid="stMetricDelta"] { font-size: 0.72rem !important; }

    /* Button */
    .stButton > button {
        background: #ffffff; color: #000000; border: none;
        font-size: 0.8375rem; font-weight: 600; padding: 9px 22px;
        border-radius: 6px; letter-spacing: -0.01em;
        transition: background 0.12s, opacity 0.12s;
        touch-action: manipulation;
    }
    .stButton > button:hover  { background: #e5e5e5; }
    .stButton > button:active { background: #d4d4d4; }
    .stButton > button:focus-visible { outline: 2px solid #3b82f6; outline-offset: 2px; }

    /* Text input */
    .stTextInput > div > div > input {
        background: #111111 !important; color: #ededed !important;
        border: 1px solid #2a2a2a !important; border-radius: 6px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 1rem !important; padding: 8px 12px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #404040 !important;
        box-shadow: 0 0 0 2px rgba(59,130,246,0.15) !important;
    }
    .stTextInput > div > div > input::placeholder { color: #444 !important; }

    /* Selects + checkboxes */
    .stSelectbox label, .stCheckbox label { color: #888 !important; font-size: 0.8rem !important; }
    .stSelectbox > div > div {
        background: #111 !important; border: 1px solid #2a2a2a !important; color: #ededed !important;
    }

    /* Expanders */
    details summary {
        background: #111 !important; border: 1px solid #1f1f1f !important;
        border-radius: 6px !important; color: #888 !important;
        font-size: 0.8rem !important; padding: 8px 12px !important;
    }
    details[open] summary { border-radius: 6px 6px 0 0 !important; }
    details > div {
        background: #0d0d0d !important; border: 1px solid #1f1f1f !important;
        border-top: none !important; border-radius: 0 0 6px 6px !important;
    }

    /* Tables */
    thead th {
        color: #555 !important; font-size: 0.72rem !important; font-weight: 600 !important;
        text-transform: uppercase !important; letter-spacing: 0.06em !important;
        border-bottom: 1px solid #1f1f1f !important;
    }
    tbody td {
        color: #ccc !important; font-size: 0.825rem !important;
        font-family: 'JetBrains Mono', monospace !important;
        border-bottom: 1px solid #141414 !important;
    }
    .stTable { background: #0d0d0d !important; }

    /* Code */
    code {
        background: #1a1a1a; color: #a3e635; padding: 1px 5px;
        border-radius: 3px; font-family: 'JetBrains Mono', monospace;
        font-size: 0.85em;
    }

    /* Trace */
    .trace-path {
        font-family: 'JetBrains Mono', monospace; font-size: 0.875rem;
        line-height: 2.6; padding: 12px 0;
    }
    .t-active  { color: #000; background: #fff; border-radius: 4px; padding: 2px 8px; font-weight: 600; }
    .t-visited { color: #3b82f6; }
    .t-pending { color: #333; }
    .t-arrow   { color: #333; }

    /* Verdict */
    .verdict {
        text-align: center; padding: 14px 24px; border-radius: 6px;
        font-family: 'JetBrains Mono', monospace; font-size: 0.95rem;
        font-weight: 500; margin-top: 1rem;
    }
    .verdict-accept { background: #050f05; border: 1px solid #14532d; color: #4ade80; }
    .verdict-reject { background: #0f0505; border: 1px solid #7f1d1d; color: #f87171; }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: #111; }
    ::-webkit-scrollbar-thumb { background: #2a2a2a; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #3a3a3a; }

    /* Spinner */
    .stSpinner > div { border-top-color: #3b82f6 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## Configuration")

    upload = st.file_uploader(
        "Upload JSON",
        type=["json"],
        help="Schema: config/variant_N.json",
    )

    _VARIANTS = list(range(1, 33))
    selected_variant = st.selectbox(
        "Variant",
        options=_VARIANTS,
        index=12,
        format_func=lambda v: f"Variant {v}",
        disabled=upload is not None,
    )

    st.markdown("---")

    include_dead = st.checkbox("Include dead state in DFA", value=True)
    show_grammar = st.checkbox("Show grammar productions", value=True)
    show_table = st.checkbox("Show construction table", value=True)

    st.markdown("---")
    _src = "Uploaded file" if upload is not None else f"Variant {selected_variant}"
    st.markdown(
        f"<p style='color:#444;font-size:0.72rem;line-height:2'>"
        f"State-Space Compiler<br>Lab 2 &middot; Formal Languages<br>{_src}</p>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# NDFA loaders
# ---------------------------------------------------------------------------
def _parse_ndfa_obj(obj: dict) -> NDFA:
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
def load_ndfa_from_bytes(data: bytes) -> NDFA:
    return _parse_ndfa_obj(json.loads(data))


@st.cache_data
def load_variant_ndfa(n: int) -> NDFA:
    path = f"config/variant_{n}.json"
    if not os.path.exists(path):
        path = f"config/variant_{n}_ndfa.json"
    with open(path) as fh:
        return _parse_ndfa_obj(json.load(fh))


# Clear compiled DFA when variant changes
_prev = st.session_state.get("_loaded_variant")
if upload is None and _prev != selected_variant:
    st.session_state["dfa"] = None
    st.session_state["_loaded_variant"] = selected_variant

ndfa: NDFA = (
    load_ndfa_from_bytes(upload.read())
    if upload is not None
    else load_variant_ndfa(selected_variant)
)


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
_label = "Uploaded File" if upload is not None else f"Variant {selected_variant}"
st.markdown(
    f"<h1>State-Space Compiler</h1>"
    f"<p style='color:#555;font-size:0.8rem;letter-spacing:0.02em;margin-top:2px'>"
    f"NDFA to DFA &nbsp;&middot;&nbsp; {_label}"
    f"</p>",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# 01 · Overview
# ---------------------------------------------------------------------------
st.markdown("## 01 &nbsp; Overview")

det = ndfa.is_deterministic()
conflicts = ndfa.non_deterministic_sources()
n_conf = len(conflicts)

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("States", len(ndfa.states))
with c2:
    st.metric("Alphabet", len(ndfa.alphabet))
with c3:
    st.metric("Transitions", sum(len(v) for v in ndfa.transitions.values()))

if det:
    st.markdown(
        '<div class="banner banner-ok"><strong>Deterministic</strong> — no ambiguous transitions</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f'<div class="banner banner-error">'
        f"<strong>Non-deterministic</strong>"
        f" &mdash; {n_conf} ambiguous transition{'s' if n_conf != 1 else ''}"
        f"</div>",
        unsafe_allow_html=True,
    )
    with st.expander("Conflict details"):
        rows = []
        for s, sym in conflicts:
            targets = sorted(ndfa.transitions[(s, sym)])
            rows.append(
                {
                    "State": s,
                    "Symbol": sym,
                    "Targets": "{" + ", ".join(targets) + "}",
                    "Count": len(targets),
                }
            )
        st.table(rows)

with st.expander("Transition table"):
    rows = []
    for (state, sym), targets in sorted(ndfa.transitions.items()):
        rows.append(
            {
                "From": state,
                "On": sym,
                "To": "{" + ", ".join(sorted(targets)) + "}",
                "Ambiguous": "yes" if len(targets) > 1 else "",
            }
        )
    st.table(rows)


# ---------------------------------------------------------------------------
# 02 · Transition Graph
# ---------------------------------------------------------------------------
st.markdown("## 02 &nbsp; Transition Graph")
st.markdown(
    "<p>Drag nodes to rearrange. Conflict states are highlighted in red.</p>",
    unsafe_allow_html=True,
)

ndfa_html = ndfa_to_html(ndfa, highlight_conflicts=True)
components.html(ndfa_html, height=480, scrolling=False)


# ---------------------------------------------------------------------------
# 03 · Grammar Analysis
# ---------------------------------------------------------------------------
st.markdown("## 03 &nbsp; Grammar Analysis")

grammar_prods = ndfa.to_grammar()
grammar = Grammar.from_fa_productions(
    non_terminals=set(ndfa.states),
    terminals=set(ndfa.alphabet),
    start=ndfa.start,
    productions=grammar_prods,
)
_, type_label, evidence = grammar.classify_chomsky()

st.markdown(
    f'<div class="banner banner-info">'
    f"Grammar extracted from NDFA &mdash; <strong>{type_label}</strong>"
    f"</div>",
    unsafe_allow_html=True,
)

if show_grammar:
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        with st.expander("Productions"):
            for lhs, rhs in grammar_prods:
                st.markdown(f"- `{lhs}` &rarr; `{rhs if rhs else 'ε'}`")
    with col_g2:
        with st.expander("Chomsky proof"):
            for line in evidence:
                st.markdown(f"- {line}")


# ---------------------------------------------------------------------------
# 04 · Subset Construction
# ---------------------------------------------------------------------------
st.markdown("## 04 &nbsp; Subset Construction")
st.markdown(
    "<p>Run the powerset algorithm to convert the NDFA into an equivalent "
    "deterministic automaton.</p>",
    unsafe_allow_html=True,
)

if "dfa" not in st.session_state:
    st.session_state["dfa"] = None

_btn_col, _ = st.columns([1, 3])
with _btn_col:
    compile_btn = st.button("Run Subset Construction", use_container_width=True)

if compile_btn:
    with st.spinner("Building DFA\u2026"):
        st.session_state["dfa"] = powerset_construction(ndfa, include_dead=include_dead)

dfa: Optional[DFA] = st.session_state.get("dfa")

if dfa is not None:
    worst = 2 ** len(ndfa.states)
    pruned = worst - len(dfa.states)

    st.markdown(
        f'<div class="banner banner-ok">'
        f"DFA generated &mdash; <strong>{len(dfa.states)}</strong> states"
        f" &nbsp;&middot;&nbsp; {pruned} of {worst} macro-states pruned"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.markdown("")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("DFA States", len(dfa.states))
    with m2:
        st.metric("Accepting States", len(dfa.accepting))
    with m3:
        st.metric("DFA Transitions", len(dfa.transitions))
    with m4:
        st.metric(
            f"Pruned (2^{len(ndfa.states)}={worst})",
            pruned,
            delta=f"-{pruned} states",
            delta_color="normal",
        )

    # Side-by-side
    st.markdown("### Comparison")
    g_left, g_right = st.columns(2)
    with g_left:
        st.markdown("**NDFA** — non-deterministic")
        components.html(ndfa_html, height=440, scrolling=False)
    with g_right:
        st.markdown("**DFA** — deterministic")
        dfa_html_base = dfa_to_html(dfa)
        components.html(dfa_html_base, height=440, scrolling=False)

    # Construction table
    if show_table:
        with st.expander("Construction table", expanded=True):
            steps = dfa.construction_steps  # type: ignore[attr-defined]
            table_data = []
            for step in steps:
                row = {"Macro-state": step["macro_state"]}
                for sym in dfa.alphabet:
                    row[sym] = step["transitions"].get(sym, "—")
                row["Accepting"] = "yes" if step["macro_state"] in dfa.accepting else ""
                table_data.append(row)
            st.table(table_data)

    with st.expander("DFA transition table"):
        dfa_rows = []
        for (state, sym), tgt in sorted(dfa.transitions.items()):
            dfa_rows.append({"From": state, "On": sym, "To": tgt})
        st.table(dfa_rows)

    # DFA grammar
    st.markdown("### DFA Grammar")
    dfa_prods = dfa.to_grammar()
    dfa_grammar = Grammar.from_fa_productions(
        non_terminals=set(dfa.states),
        terminals=set(dfa.alphabet),
        start=dfa.start,
        productions=dfa_prods,
    )
    _, dfa_type_label, _ = dfa_grammar.classify_chomsky()
    st.markdown(
        f'<div class="banner banner-info">'
        f"DFA grammar &mdash; <strong>{dfa_type_label}</strong>"
        f" &nbsp;&middot;&nbsp; classification preserved"
        f"</div>",
        unsafe_allow_html=True,
    )

    # -------------------------------------------------------------------------
    # 05 · String Tester
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("## 05 &nbsp; String Tester")
    st.markdown(
        "<p>Trace a string through the DFA. Advance the step slider to replay "
        "state transitions one symbol at a time.</p>",
        unsafe_allow_html=True,
    )

    t_col, s_col = st.columns([2, 1])
    with t_col:
        test_string = st.text_input(
            "Input string",
            value="",
            placeholder="e.g. abab\u2026",
            label_visibility="collapsed",
        )
    with s_col:
        step = (
            st.slider("Step", 0, len(test_string), len(test_string))
            if test_string
            else 0
        )

    if test_string:
        accepted, full_path = dfa.trace(test_string)

        # Trace path
        path_parts: List[str] = []
        for i, state in enumerate(full_path):
            if i == step:
                path_parts.append(f'<span class="t-active">{state}</span>')
            elif i < step:
                path_parts.append(f'<span class="t-visited">{state}</span>')
            else:
                path_parts.append(f'<span class="t-pending">{state}</span>')
            if i < len(full_path) - 1:
                sym = test_string[i] if i < len(test_string) else ""
                path_parts.append(f'<span class="t-arrow"> [{sym}]&rarr; </span>')

        st.markdown(
            '<div class="trace-path">' + "".join(path_parts) + "</div>",
            unsafe_allow_html=True,
        )

        # Highlighted graph at current step
        active = full_path[step] if step < len(full_path) else full_path[-1]
        traced = full_path[: step + 1]
        components.html(
            dfa_to_html(dfa, active_state=active, trace_path=traced),
            height=460,
            scrolling=False,
        )

        # Verdict (shown at last step only)
        if step == len(test_string):
            if accepted:
                st.markdown(
                    f'<div class="verdict verdict-accept">'
                    f"{test_string!r} &mdash; ACCEPTED &nbsp;&middot;&nbsp; "
                    f"final state: {full_path[-1]}"
                    f"</div>",
                    unsafe_allow_html=True,
                )
            else:
                note = " (dead state)" if full_path[-1] == dfa.DEAD_LABEL else ""
                st.markdown(
                    f'<div class="verdict verdict-reject">'
                    f"{test_string!r} &mdash; REJECTED{note} &nbsp;&middot;&nbsp; "
                    f"final state: {full_path[-1]}"
                    f"</div>",
                    unsafe_allow_html=True,
                )

else:
    st.markdown(
        '<div class="banner banner-info">'
        "Click <strong>Run Subset Construction</strong> above to compile the NDFA into a DFA."
        "</div>",
        unsafe_allow_html=True,
    )
