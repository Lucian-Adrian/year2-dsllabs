"""
Visualizer — Layer 5: Interactive Graph Renderer.

Generates interactive, physics-based HTML graphs using PyVis.
The HTML is returned as a string and can be embedded in the Streamlit
dashboard via st.components.v1.html().

Node colour legend
------------------
  Start state         : dodgerblue border, light blue fill
  Accepting state     : green border, light-green fill
  Non-deterministic   : red/orange fill  (NDFA only — conflict nodes)
  Active (live trace) : gold fill
  Dead/trap state ∅   : grey
  Regular state       : white fill, dark border
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional, Set

from pyvis.network import Network

if TYPE_CHECKING:
    from .ndfa import NDFA
    from .powerset import DFA


# ---------------------------------------------------------------------------
# Shared builder helpers
# ---------------------------------------------------------------------------

def _new_net(height: str = "500px", physics: bool = True) -> Network:
    # cdn_resources="in_line" embeds vis.js directly in the HTML blob.
    # This avoids (a) CDN permission-policy warnings in Streamlit iframes and
    # (b) the "Unexpected identifier 'Streamlit'" SyntaxError that appears when
    # Streamlit's component host tries to inject utils.js into an iframe that
    # is also loading remote scripts with conflicting scoping.
    try:
        net = Network(
            height=height,
            width="100%",
            directed=True,
            bgcolor="#0a0a0a",
            font_color="#ededed",
            cdn_resources="in_line",
        )
    except TypeError:
        # Older pyvis versions don't have cdn_resources
        net = Network(
            height=height,
            width="100%",
            directed=True,
            bgcolor="#0a0a0a",
            font_color="#ededed",
        )
    if physics:
        net.force_atlas_2based(
            gravity=-50,
            central_gravity=0.01,
            spring_length=200,
            spring_strength=0.05,
            damping=0.4,
        )
    return net


def _node_style(
    label: str,
    is_start: bool,
    is_accepting: bool,
    is_conflict: bool = False,
    is_active: bool = False,
    is_dead: bool = False,
) -> Dict:
    """Return PyVis node kwargs."""
    if is_dead:
        color = {"border": "#333", "background": "#1a1a1a", "highlight": {"background": "#222"}}
        shape = "dot"
    elif is_active:
        color = {"border": "#ffffff", "background": "#ffffff", "highlight": {"background": "#ededed"}}
        shape = "ellipse"
    elif is_conflict:
        color = {"border": "#dc2626", "background": "#450a0a", "highlight": {"background": "#7f1d1d"}}
        shape = "ellipse"
    elif is_accepting and is_start:
        color = {"border": "#16a34a", "background": "#052e16", "highlight": {"background": "#14532d"}}
        shape = "ellipse"
    elif is_accepting:
        color = {"border": "#16a34a", "background": "#052e16", "highlight": {"background": "#14532d"}}
        shape = "ellipse"
    elif is_start:
        color = {"border": "#2563eb", "background": "#03173a", "highlight": {"background": "#1e3a6e"}}
        shape = "ellipse"
    else:
        color = {"border": "#404040", "background": "#1a1a1a", "highlight": {"background": "#262626"}}
        shape = "ellipse"

    border_width = 2 if (is_start or is_accepting) else 1
    font_color = "#000000" if is_active else "#ededed"
    return {
        "color": color,
        "shape": shape,
        "size": 28,
        "font": {"size": 14, "color": font_color},
        "borderWidth": border_width,
        "borderWidthSelected": 3,
    }


def _merge_edge_labels(transitions: dict) -> Dict:
    """Merge multiple transitions into single edges with combined label.
    Handles both NDFA (frozenset targets) and DFA (string targets)."""
    edge_map: Dict = {}
    for (src, sym), tgt in transitions.items():
        # NDFA: tgt is frozenset; DFA: tgt is a string
        targets = tgt if isinstance(tgt, (frozenset, set)) else {tgt}
        for t in targets:
            key = (src, t)
            edge_map.setdefault(key, []).append(sym)
    return {k: ",".join(sorted(v)) for k, v in edge_map.items()}


# ---------------------------------------------------------------------------
# NDFA visualisation
# ---------------------------------------------------------------------------

def ndfa_to_html(
    ndfa: "NDFA",
    active_state: Optional[str] = None,
    highlight_conflicts: bool = True,
    height: str = "480px",
) -> str:
    """Render NDFA as interactive HTML string (for Streamlit embedding)."""
    net = _new_net(height=height)

    conflict_states: Set[str] = set()
    if highlight_conflicts:
        for state, _ in ndfa.non_deterministic_sources():
            conflict_states.add(state)

    for s in ndfa.states:
        kwargs = _node_style(
            label=s,
            is_start=(s == ndfa.start),
            is_accepting=(s in ndfa.accepting),
            is_conflict=(s in conflict_states),
            is_active=(s == active_state),
        )
        net.add_node(s, label=s, **kwargs)

    merged = _merge_edge_labels(ndfa.transitions)
    for (src, tgt), lbl in merged.items():
        net.add_edge(
            src, tgt, label=lbl,
            color="#555555", width=1,
            font={"size": 12, "color": "#999999"},
            arrows="to",
        )

    return net.generate_html()


# ---------------------------------------------------------------------------
# DFA visualisation (with optional active-state trace)
# ---------------------------------------------------------------------------

def dfa_to_html(
    dfa: "DFA",
    active_state: Optional[str] = None,
    trace_path: Optional[List[str]] = None,
    height: str = "480px",
) -> str:
    """Render DFA as interactive HTML string."""
    net = _new_net(height=height)

    trace_set: Set[str] = set(trace_path) if trace_path else set()

    for s in dfa.states:
        is_dead = s == dfa.DEAD_LABEL
        kwargs = _node_style(
            label=s,
            is_start=(s == dfa.start),
            is_accepting=(s in dfa.accepting),
            is_active=(s == active_state),
            is_dead=is_dead,
        )
        # Add faint tint for visited-but-not-current states in trace
        if trace_path and s in trace_set and s != active_state:
            kwargs["color"] = {
                "border": "#2563eb",
                "background": "#0c1a3a",
                "highlight": {"background": "#1e3a6e"},
            }
        net.add_node(s, label=s, **kwargs)

    merged = _merge_edge_labels(dfa.transitions)
    for (src, tgt), lbl in merged.items():
        if tgt == dfa.DEAD_LABEL and active_state is None:
            edge_color = "#2a2a2a"
        else:
            edge_color = "#555555"
        net.add_edge(
            src, tgt, label=lbl,
            color=edge_color, width=1,
            font={"size": 12, "color": "#999999"},
            arrows="to",
        )

    return net.generate_html()
