from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.catalog import list_variants, load_variant_grammar
from src.cnf import CNFConverter
from src.grammar import Grammar
from src.reporting import build_report_markdown
from src.visualization import grammar_mermaid, pipeline_mermaid, production_rows, render_interactive_mermaid_html, render_mermaid_html


DEFAULT_CUSTOM_TEXT = """S -> aB
S -> DA
A -> a
A -> BD
A -> bDAB
B -> b
B -> BA
D -> ε
D -> BA
C -> BA"""


st.set_page_config(
    page_title="Lab 5 · Chomsky Normal Form",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

    :root {
        --bg: #07111f;
        --panel: #0f1b2d;
        --panel-2: #12243b;
        --line: rgba(148, 163, 184, 0.18);
        --accent: #38bdf8;
        --accent-2: #f59e0b;
        --text: #e5eefc;
        --muted: #94a3b8;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(56, 189, 248, 0.16), transparent 30%),
            radial-gradient(circle at top right, rgba(245, 158, 11, 0.14), transparent 24%),
            linear-gradient(180deg, #06111f 0%, #07111f 48%, #050b14 100%);
        color: var(--text);
        font-family: 'IBM Plex Sans', sans-serif;
    }

    .block-container { padding-top: 1.4rem; padding-bottom: 2rem; }

    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif;
        letter-spacing: -0.03em;
        color: var(--text) !important;
    }

    h1 { font-size: 2.2rem !important; margin-bottom: 0.15rem; }
    h2 { font-size: 1.2rem !important; margin-top: 1.4rem !important; }
    h3 { font-size: 1rem !important; }

    p, li, label, span { color: var(--text); }
    code, pre { font-family: 'IBM Plex Mono', monospace !important; }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(18, 36, 59, 0.96), rgba(10, 20, 34, 0.98));
        border-right: 1px solid var(--line);
    }

    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p { color: #cbd5e1 !important; }

    [data-testid="metric-container"] {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.92), rgba(16, 27, 45, 0.92));
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 0.6rem 0.8rem;
    }

    [data-testid="stMetricValue"] {
        color: white !important;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.7rem !important;
    }

    [data-testid="stMetricLabel"] { color: var(--muted) !important; }

    .card {
        background: linear-gradient(180deg, rgba(15, 27, 45, 0.92), rgba(12, 20, 36, 0.96));
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 1rem 1.1rem;
        box-shadow: 0 18px 50px rgba(0, 0, 0, 0.24);
    }

    .hero {
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.18), rgba(245, 158, 11, 0.12));
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 20px;
        padding: 1.15rem 1.2rem;
        margin-bottom: 1rem;
    }

    .hero .eyebrow {
        display: inline-block;
        font-size: 0.74rem;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        color: var(--accent);
        margin-bottom: 0.45rem;
    }

    .hero .subtitle { color: #cbd5e1; margin-top: 0.35rem; line-height: 1.6; }

    .stButton > button,
    .stDownloadButton > button {
        background: linear-gradient(135deg, #0ea5e9, #2563eb);
        color: #f8fafc;
        border: 0;
        border-radius: 999px;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        padding: 0.55rem 1rem;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover { opacity: 0.93; }

    .stTextArea textarea,
    .stTextInput input,
    .stSelectbox div[data-baseweb="select"] > div,
    .stFileUploader {
        background: rgba(15, 27, 45, 0.95) !important;
        color: var(--text) !important;
        border-color: var(--line) !important;
    }

    details summary {
        background: rgba(15, 27, 45, 0.92) !important;
        color: #dbeafe !important;
        border: 1px solid var(--line) !important;
        border-radius: 12px !important;
    }

    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-thumb { background: rgba(56, 189, 248, 0.32); border-radius: 999px; }
    </style>
    """,
    unsafe_allow_html=True,
)


def _load_uploaded_grammar(uploaded) -> Grammar:
    raw = uploaded.getvalue().decode("utf-8")
    if uploaded.name.lower().endswith(".json"):
        data = json.loads(raw)
        return Grammar.from_json_dict(data)
    return Grammar.from_text(raw)


def _convert(grammar: Grammar):
    return CNFConverter().convert(grammar)


def _ensure_step_index(step_count: int) -> int:
    if step_count <= 0:
        st.session_state.cnf_step_index = 0
        return 0

    current = int(st.session_state.get("cnf_step_index", 0))
    current = max(0, min(current, step_count - 1))
    st.session_state.cnf_step_index = current
    return current


def _step_theory(step_title: str, step_description: str, notes: tuple[str, ...]) -> list[str]:
    title = step_title.lower()
    lines: list[str] = []

    if "augment start" in title:
        lines.append("A fresh start symbol makes the later ε-elimination safe because the original start symbol can still be referenced without violating the CNF restriction.")
    elif "ε-productions" in title:
        lines.append("Nullable symbols are expanded combinatorially so every string that was possible before still has a surviving derivation after ε rules are removed.")
    elif "unit productions" in title:
        lines.append("Unit-production chains are collapsed into direct non-unit productions, removing redundant hops while keeping the same terminal language.")
    elif "useless symbols" in title or "cleanup" in title:
        lines.append("Unproductive and unreachable symbols are trimmed because they cannot appear in any valid derivation from the start symbol.")
    elif "isolate terminals" in title:
        lines.append("Fresh helper symbols stand in for terminals inside long rules so the grammar matches the CNF shape A -> BC or A -> a.")
    elif "binarize" in title:
        lines.append("Long productions are split into binary chains so the final grammar satisfies the structural part of CNF exactly.")
    else:
        lines.append(step_description)

    if notes:
        lines.append("What to notice:")
        lines.extend(f"- {note}" for note in notes)

    return lines


st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">Formal Languages &amp; Finite Automata · Lab 5</div>
      <h1>Chomsky Normal Form, fully traced.</h1>
      <div class="subtitle">
        Convert the official grammar variants or paste your own grammar, inspect each rewrite pass,
        and export a report bundle with visuals.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## Input")
    upload = st.file_uploader("Upload grammar JSON or text", type=["json", "txt", "md"], help="Optional override for the official catalog.")
    variant_choice = st.selectbox(
        "Official variant",
        options=list_variants(),
        index=list_variants().index(13) if 13 in list_variants() else 0,
        format_func=lambda value: f"Variant {value}",
        disabled=upload is not None,
    )
    use_custom_text = st.checkbox("Paste custom grammar", value=False, disabled=upload is not None)
    custom_text = st.text_area("Custom grammar", value=DEFAULT_CUSTOM_TEXT, height=220, disabled=upload is not None or not use_custom_text)
    st.markdown("---")
    show_raw = st.checkbox("Show raw productions", value=True)
    show_steps = st.checkbox("Show rewrite trace", value=True)
    st.markdown("---")
    st.caption("Variant 13 is the default because it also showed up in the earlier labs, but the converter works for any of the 32 official grammars.")


source_label = ""
if upload is not None:
    grammar = _load_uploaded_grammar(upload)
    source_label = upload.name
elif use_custom_text:
    grammar = Grammar.from_text(custom_text)
    source_label = "Custom grammar"
else:
    grammar = load_variant_grammar(variant_choice)
    source_label = f"Variant {variant_choice}"

result = _convert(grammar)
active_step = _ensure_step_index(len(result.steps))

if not result.is_valid():
    st.error("The final grammar still has CNF issues. The conversion pipeline needs review.")
else:
    st.success("CNF verified for the final grammar.")

metrics = st.columns(4)
with metrics[0]:
    st.metric("Original productions", grammar.production_count())
with metrics[1]:
    st.metric("Final productions", result.final.production_count())
with metrics[2]:
    st.metric("Helper symbols", len(result.helper_symbols))
with metrics[3]:
    st.metric("Steps", len(result.steps))

tabs = st.tabs(["Overview", "Steps", "Theory", "CNF Proof", "Export"])

with tabs[0]:
    left, right = st.columns([1.15, 0.85], gap="large")
    with left:
        st.markdown("### Source Grammar")
        st.caption("Rendered as plain text for compatibility, so this view does not depend on pyarrow or pandas.")
        if show_raw:
            raw_lines = [
                f"{row['#']}. {row['LHS']} -> {row['RHS']} [{row['Kind']}]"
                for row in production_rows(grammar)
            ]
            st.code("\n".join(raw_lines), language="text")
        st.code(grammar.pretty(), language="text")
    with right:
        st.markdown("### Pipeline Visual")
        st.caption("The highlighted node follows the manual stepper below. The canvas supports drag, wheel zoom, and fit-to-screen.")
        components.html(
            render_interactive_mermaid_html(
                pipeline_mermaid(result, active_step=active_step),
                title=f"{source_label} pipeline",
                height=760,
            ),
            height=820,
            scrolling=False,
        )

with tabs[1]:
    st.markdown("### Manual Stepper")
    st.caption("Move one rewrite at a time to see exactly what changed and why the pass is valid.")

    if result.steps:
        nav_left, nav_mid, nav_right = st.columns([0.9, 1.4, 0.9])
        with nav_left:
            if st.button("Previous step", disabled=active_step <= 0, use_container_width=True):
                st.session_state.cnf_step_action = "prev"
                st.rerun()
        with nav_mid:
            # Process any pending step action BEFORE rendering the slider
            # This avoids the Streamlit session_state mutation error
            if "cnf_step_action" in st.session_state:
                action = st.session_state.cnf_step_action
                if action == "prev" and active_step > 0:
                    st.session_state.cnf_step_index = active_step - 1
                elif action == "next" and active_step < len(result.steps) - 1:
                    st.session_state.cnf_step_index = active_step + 1
                del st.session_state.cnf_step_action
                st.rerun()

            st.slider(
                "Selected rewrite",
                min_value=0,
                max_value=len(result.steps) - 1,
                key="cnf_step_index",
                format="Step %d",
            )
        with nav_right:
            if st.button("Next step", disabled=active_step >= len(result.steps) - 1, use_container_width=True):
                st.session_state.cnf_step_action = "next"
                st.rerun()

        step = result.steps[active_step]
        st.markdown(f"#### Step {active_step + 1}: {step.title}")
        st.write(step.description)
        if step.notes:
            for note in step.notes:
                st.caption(note)

        summary_left, summary_right = st.columns([1, 1], gap="large")
        with summary_left:
            st.markdown("**What changed**")
            if step.added:
                st.caption(f"Added {len(step.added)} production(s).")
                st.code("\n".join(str(production) for production in step.added[:20]), language="text")
            else:
                st.caption("No new productions were added in this pass.")
            if step.removed:
                st.caption(f"Removed {len(step.removed)} production(s).")
                st.code("\n".join(str(production) for production in step.removed[:20]), language="text")
            else:
                st.caption("No productions were removed in this pass.")

        with summary_right:
            st.markdown("**Why it works**")
            explanation_lines = [
                f"The pass is valid because it transforms {step.before.production_count()} production(s) into {step.after.production_count()} production(s) without changing the grammar model.",
                "Each pass preserves reachability, trims illegal forms, or introduces helper symbols only when needed.",
                "The pipeline stays correct because the next pass always consumes the cleaned grammar produced here.",
            ]
            st.write("\n".join(explanation_lines))

        st.markdown("#### Theory breakdown")
        st.write("\n".join(_step_theory(step.title, step.description, step.notes)))

        before_col, after_col = st.columns(2, gap="large")
        with before_col:
            st.markdown("**Before**")
            st.code(step.before.pretty(), language="text")
        with after_col:
            st.markdown("**After**")
            st.code(step.after.pretty(), language="text")

        st.markdown("#### Remaining trace")
        trace_lines = []
        for index, item in enumerate(result.steps, start=1):
            status = "active" if index - 1 == active_step else "done" if index - 1 < active_step else "pending"
            trace_lines.append(f"{index}. {item.title} — {status}")
        st.code("\n".join(trace_lines), language="text")
    else:
        st.info("No rewrite steps were produced for this grammar.")

with tabs[2]:
    st.markdown("### Theory Walkthrough")
    st.caption("This section explains the full CNF conversion in the order the converter applies it.")

    st.markdown("#### CNF rule set")
    st.write(
        """
        CNF allows only three production shapes: A -> BC, A -> a, and S -> ε when the start symbol does not appear on the right-hand side.
        The converter first cleans the grammar, then isolates terminals, then binarizes long rules so every remaining production fits one of those forms.
        """
    )

    st.markdown("#### Why the order matters")
    st.write(
        """
        ε-elimination must happen before binarization because nullable symbols can change the effective length of a rule.
        Unit productions are removed before useless-symbol cleanup so the reachability graph reflects the real language-producing structure.
        Terminal isolation and binarization happen after cleanup because helper symbols should be introduced only into the useful core of the grammar.
        """
    )

    for index, step in enumerate(result.steps, start=1):
        with st.expander(f"{index}. {step.title}", expanded=index == 1):
            st.write(step.description)
            st.markdown("**Applied theory**")
            st.write("\n".join(_step_theory(step.title, step.description, step.notes)))
            st.markdown("**Before / after relationship**")
            st.write(
                f"This pass takes {step.before.production_count()} production(s) and returns {step.after.production_count()} production(s), "
                f"preserving the generated language while reducing the grammar toward CNF."
            )
            if step.notes:
                st.markdown("**Key observations**")
                for note in step.notes:
                    st.caption(note)

    st.markdown("#### Variant atlas")
    st.caption("Pick any official variant to inspect its source grammar and a Mermaid diagram without leaving the app.")
    atlas_variant = st.selectbox(
        "Official variant atlas",
        options=list_variants(),
        index=list_variants().index(variant_choice) if variant_choice in list_variants() else 0,
        format_func=lambda value: f"Variant {value}",
        key="atlas_variant",
    )
    atlas_grammar = load_variant_grammar(atlas_variant)
    atlas_left, atlas_right = st.columns([1, 1], gap="large")
    with atlas_left:
        st.markdown("**Source grammar**")
        st.code(atlas_grammar.pretty(), language="text")
    with atlas_right:
        st.markdown("**Mermaid diagram**")
        components.html(
            render_interactive_mermaid_html(
                grammar_mermaid(atlas_grammar, f"Variant {atlas_variant} source grammar"),
                title=f"Variant {atlas_variant} grammar diagram",
                height=620,
            ),
            height=680,
            scrolling=False,
        )

with tabs[3]:
    if result.is_valid():
        st.markdown("### CNF checklist")
        st.success("Every production now matches one of the CNF shapes: A → BC, A → a, or S → ε.")
        st.code(result.final.pretty(), language="text")
    else:
        st.error("CNF validation failed.")
        for issue in result.issues:
            st.write(f"- {issue}")

with tabs[4]:
    report_markdown = build_report_markdown(f"Lab 5 · {source_label}", grammar, result)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.download_button(
            "Download report.md",
            data=report_markdown,
            file_name=f"{source_label.replace(' ', '_').lower()}_report.md",
            mime="text/markdown",
            width="stretch",
        )
    with col2:
        st.download_button(
            "Download final grammar",
            data=result.final.pretty(),
            file_name=f"{source_label.replace(' ', '_').lower()}_final_grammar.txt",
            mime="text/plain",
            width="stretch",
        )
    with col3:
        st.download_button(
            "Download pipeline.mmd",
            data=pipeline_mermaid(result),
            file_name=f"{source_label.replace(' ', '_').lower()}_pipeline.mmd",
            mime="text/plain",
            width="stretch",
        )
    with col4:
        st.download_button(
            "Download result.json",
            data=json.dumps(
                {
                    "source": source_label,
                    "original": grammar.summary(),
                    "final": result.final.summary(),
                    "issues": list(result.issues),
                    "helpers": list(result.helper_symbols),
                    "steps": [
                        {
                            "title": step.title,
                            "description": step.description,
                            "notes": list(step.notes),
                        }
                        for step in result.steps
                    ],
                },
                indent=2,
                ensure_ascii=False,
            ),
            file_name=f"{source_label.replace(' ', '_').lower()}_result.json",
            mime="application/json",
            width="stretch",
        )

