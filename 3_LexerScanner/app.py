import time

import altair as alt
import pandas as pd
import streamlit as st
from streamlit_ace import st_ace  # rich code editor

# graphviz is optional; the dashboard will still work without it
try:
    import graphviz
except ImportError:  # fallback if package or binary is missing
    graphviz = None
from typing import List

from src.highlighter import count_tokens_by_type
from src.lexer import LexicalError, iter_tokens
from src.tokens import Token

# ==============================================================================
# 0. CONFIGURATION & STYLING
# ==============================================================================
st.set_page_config(
    page_title="TensorScript Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for that "famous, overachieved" look
st.markdown(
    """
<style>
    .stApp { background-color: #fafbfc; font-family: 'Inter', sans-serif; }
    h1 {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem !important;
        margin-bottom: -10px;
    }
    .subtitle { color: #64748b; font-size: 1.1rem; margin-bottom: 20px; font-weight: 500; }
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        background: linear-gradient(90deg, #10b981 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    .error-card {
        background: #fef2f2; border-left: 6px solid #ef4444; padding: 1rem;
        border-radius: 4px; color: #991b1b; font-family: monospace;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 1. STATE & DATA PROCESSING
# ==============================================================================
DEFAULT_CODE = """// TensorScript Advanced Demo
def activate(x) {
    return relu(x);
}

let input = [1.0, -0.5, 2.3]; // Neural payload
let state = activate(input);
let scalar = 42;
"""

if "source_code" not in st.session_state:
    st.session_state.source_code = DEFAULT_CODE


def process_code(code: str):
    tokens = []
    error = None
    start_time = time.perf_counter()
    try:
        tokens = list(iter_tokens(code, source_name="<editor>", emit_comments=True))
    except LexicalError as e:
        error = e
    except Exception as e:
        error = str(e)
    end_time = time.perf_counter()
    return tokens, error, (end_time - start_time)


# ==============================================================================
# 2. UI LAYOUT
# ==============================================================================
st.title("TensorScript Studio ✨")
st.markdown(
    "<p class='subtitle'>The Ultimate Next-Gen Lexical Observatory. SOLID. Fast. Perfect.</p>",
    unsafe_allow_html=True,
)

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 📝 Code Editor")
    with st.container(border=True):
        # use ace editor for nicer experience
        new_code = st_ace(
            value=st.session_state.source_code,
            language="javascript",  # close enough for TensorScript syntax
            theme="github",
            height=300,
            key="ace_editor",
        )
        col_btn1, col_btn2, _ = st.columns([1, 1, 3])
        with col_btn1:
            if st.button("🚀 Lex File", use_container_width=True, type="primary"):
                st.session_state.source_code = new_code
        with col_btn2:
            if st.button("🧹 Clear", use_container_width=True):
                st.session_state.source_code = ""
                st.rerun()

    code_to_process = st.session_state.source_code

tokens, error, duration = process_code(code_to_process)

with col1:
    if error:
        st.markdown("### 🚨 Diagnostics: Lexical Error Found!")
        if isinstance(error, LexicalError):
            st.markdown(
                f'<div class="error-card"><b>Error:</b> {error.message}<br/><b>Lexeme:</b> <code>{error.offending_lexeme}</code><br/><b>Position:</b> Line {error.line}, Col {error.column}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.error(f"Unexpected Exception: {error}")
    else:
        st.success(
            f"Lexical Analysis successful! Processed in {duration * 1000:.2f} ms ⚡"
        )

# ==============================================================================
# 3. OBSERVATORY DASHBOARD
# ==============================================================================
with col2:
    st.markdown("### 📊 Live Analytics")
    if tokens:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Tokens", len(tokens))
        m2.metric("Comments", sum(1 for t in tokens if t.token_type.name == "COMMENT"))
        m3.metric(
            "Keywords",
            sum(1 for t in tokens if t.token_type.name in ("KEYWORD", "MATH_FUNCTION")),
        )
        m4.metric(
            "Identifiers", sum(1 for t in tokens if t.token_type.name == "IDENTIFIER")
        )

        st.markdown("#### Token Distribution by Category")
        token_types = count_tokens_by_type(tokens)
        df_tokens = pd.DataFrame(
            [{"Type": t, "Count": c} for t, c in token_types.items() if c > 0]
        )

        if not df_tokens.empty:
            chart = (
                alt.Chart(df_tokens)
                .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
                .encode(
                    x=alt.X("Type:N", sort="-y", title="Token Type"),
                    y=alt.Y("Count:Q", title="Frequency"),
                    color=alt.Color(
                        "Type:N", legend=None, scale=alt.Scale(scheme="set2")
                    ),
                    tooltip=["Type", "Count"],
                )
                .properties(height=250)
            )
            st.altair_chart(chart, use_container_width=True)
    else:
        st.info("Awaiting valid code to generate analytics.")

    # allow users to download tokens JSON
    if tokens:
        import json
        json_bytes = json.dumps([t.__dict__ for t in tokens], default=str, indent=2).encode('utf-8')
        st.download_button(
            "📥 Download Tokens (JSON)",
            data=json_bytes,
            file_name="tokens.json",
            mime="application/json",
        )

st.divider()

# ==============================================================================
# 4. DEEP DIVE TABS
# ==============================================================================
if tokens:
    # adjust tab label if graphviz isn't available
    tab_labels = ["🗂️ Token Catalog", "📜 SOLID Architecture"]
    if graphviz is not None:
        tab_labels.insert(1, "🧬 Graphviz Pipeline")
    else:
        tab_labels.insert(1, "⚠️ Graphviz Missing")
    tab1, tab2, tab3 = st.tabs(tab_labels)

    with tab1:
        data = [
            {
                "Lexeme": t.lexeme,
                "Type": t.token_type.name,
                "Value": str(t.value),
                "Line": t.span.start.line,
                "Col": t.span.start.column,
            }
            for t in tokens
        ]
        st.dataframe(pd.DataFrame(data), use_container_width=True, height=350)

    with tab2:
        if graphviz is None:
            st.warning(
                "Graphviz library not installed; install via `pip install graphviz` to view the token pipeline visualization."
            )
        else:
            try:
                dot = graphviz.Digraph(comment="Token Lifecycle")
                dot.attr(rankdir="LR", size="8,5", bgcolor="transparent")
                dot.attr(
                    "node",
                    shape="box",
                    style="filled",
                    fillcolor="#f8fafc",
                    fontname="Inter",
                    border="0",
                )
                dot.attr("edge", color="#94a3b8")

                sample_tokens = tokens[:15]
                for i, t in enumerate(sample_tokens):
                    color = (
                        "#bfdbfe"
                        if t.token_type.name == "IDENTIFIER"
                        else "#fbcfe8"
                        if t.token_type.name == "KEYWORD"
                        else "#d9f99d"
                    )
                    dot.node(
                        f"node{i}",
                        f"{t.lexeme}\\n[{t.token_type.name}]",
                        fillcolor=color,
                    )
                    if i > 0:
                        dot.edge(f"node{i - 1}", f"node{i}")

                if len(tokens) > 15:
                    dot.node(
                        "more",
                        f"... {len(tokens) - 15} more",
                        shape="none",
                        fillcolor="none",
                    )
                    dot.edge(f"node14", "more")

                st.graphviz_chart(dot.source, use_container_width=True)
            except Exception:
                st.warning("Graphviz rendering failed. Ensure 'dot' binary is on PATH.")

    with tab3:
        st.markdown("""
        ### The TensorScript Lexer SOLID Architecture
        - **S:** `TensorScriptLexer` isolates traversal, `tokens.py` holds definitions, `app.py` renders state.
        - **O:** Config-driven parsing (`LexerConfig`). You can change rules without rewriting `lexer.py` core functions.
        - **L:** Subclassed `LexicalError` integrates gracefully with standard Python Exception handling.
        - **I:** Memory-efficient stream $O(1)$ generators (`iter_tokens`) instead of monolithic lists.
        - **D:** Uses abstracted representations for mapping `TokenType` enumerators rather than raw strings for flow-control.
        """)
