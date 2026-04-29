from __future__ import annotations

from typing import Iterable

from .cnf import CNFConversionResult
from .grammar import Grammar, Production


def format_grammar_block(grammar: Grammar) -> str:
    return grammar.pretty()


def production_rows(grammar: Grammar) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for index, production in enumerate(grammar.productions, start=1):
        kind = (
            "ε"
            if not production.rhs
            else "terminal"
            if len(production.rhs) == 1
            else "binary"
            if len(production.rhs) == 2
            else "long"
        )
        rows.append(
            {
                "#": str(index),
                "LHS": production.lhs,
                "RHS": "ε" if not production.rhs else " ".join(production.rhs),
                "Kind": kind,
            }
        )
    return rows


def _node_label(text: str) -> str:
    return text.replace("\n", "<br/>")


def pipeline_mermaid(result: CNFConversionResult, active_step: int | None = None) -> str:
    lines = ["flowchart LR"]
    lines.append("    classDef stage fill:#10233b,stroke:#38bdf8,color:#e2e8f0,stroke-width:1px;")
    lines.append("    classDef done fill:#083344,stroke:#0ea5e9,color:#cffafe,stroke-width:1px;")
    lines.append("    classDef current fill:#78350f,stroke:#f59e0b,color:#fffbeb,stroke-width:2px;")
    lines.append("    classDef success fill:#052e1a,stroke:#22c55e,color:#dcfce7,stroke-width:1px;")

    stages = [("S0", f"Original\n{result.original.production_count()} productions")]
    for index, step in enumerate(result.steps, start=1):
        stages.append(
            (
                f"S{index}",
                f"{step.title}\n{step.after.production_count()} productions",
            )
        )

    for node_id, label in stages:
        lines.append(f'    {node_id}["{_node_label(label)}"]')

    for index in range(len(stages) - 1):
        lines.append(f"    {stages[index][0]} --> {stages[index + 1][0]}")

    if active_step is None:
        active_stage = len(stages) - 1
    else:
        active_stage = max(0, min(active_step + 1, len(stages) - 1))

    for index, (node_id, _) in enumerate(stages):
        if index < active_stage:
            lines.append(f"    class {node_id} done;")
        elif index == active_stage:
            lines.append(f"    class {node_id} current;")
        else:
            lines.append(f"    class {node_id} stage;")

    lines.append(f"    class {stages[-1][0]} success;")
    return "\n".join(lines)


def grammar_mermaid(grammar: Grammar, title: str) -> str:
    lines = ["flowchart TD"]
    lines.append("    classDef nt fill:#1e293b,stroke:#38bdf8,color:#e2e8f0,stroke-width:1px;")
    lines.append("    classDef prod fill:#fff7ed,stroke:#fb923c,color:#7c2d12,stroke-width:1px;")
    lines.append("    classDef term fill:#ecfccb,stroke:#84cc16,color:#3f6212,stroke-width:1px;")
    lines.append(f'    ROOT(["{_node_label(title)}"])')

    grouped: dict[str, list[Production]] = {}
    for production in grammar.productions:
        grouped.setdefault(production.lhs, []).append(production)

    for lhs, productions in grouped.items():
        lhs_id = f'N_{lhs}'
        lines.append(f'    {lhs_id}["{_node_label(lhs)}"]')
        lines.append(f"    ROOT --> {lhs_id}")
        lines.append(f"    class {lhs_id} nt;")
        for index, production in enumerate(productions, start=1):
            prod_id = f'P_{lhs}_{index}'
            rhs_label = "ε" if not production.rhs else " ".join(production.rhs)
            lines.append(f'    {prod_id}["{_node_label(rhs_label)}"]')
            lines.append(f"    {lhs_id} --> {prod_id}")
            lines.append(f"    class {prod_id} prod;")
            for token in production.rhs:
                if token in grammar.terminals:
                    term_id = f'T_{token}'
                    lines.append(f'    {term_id}["{_node_label(token)}"]')
                    lines.append(f"    {prod_id} --> {term_id}")
                    lines.append(f"    class {term_id} term;")

    return "\n".join(lines)


def step_markdown(step_title: str, before: Grammar, after: Grammar, notes: Iterable[str]) -> str:
    note_lines = "\n".join(f"- {note}" for note in notes)
    return (
        f"### {step_title}\n\n"
        f"Before: {before.production_count()} productions\n\n"
        f"After: {after.production_count()} productions\n\n"
        f"{note_lines}\n"
    )


def render_mermaid_html(markup: str) -> str:
    return f"""
<div class="mermaid">{markup}</div>
<script type="module">
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
mermaid.initialize({{ startOnLoad: true, securityLevel: 'loose', theme: 'dark' }});
</script>
"""


def render_interactive_mermaid_html(markup: str, title: str, height: int = 760) -> str:
        return f"""
<style>
    html, body {{
        margin: 0;
        padding: 0;
        width: 100%;
        height: 100%;
        overflow: hidden;
        background: transparent;
        font-family: 'IBM Plex Sans', sans-serif;
    }}
    .viewer {{
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
        gap: 10px;
        color: #e5eefc;
    }}
    .toolbar {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        align-items: center;
        justify-content: space-between;
        padding: 10px 12px;
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 14px;
        background: linear-gradient(180deg, rgba(15, 27, 45, 0.96), rgba(12, 20, 36, 0.98));
    }}
    .toolbar .title {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.92rem;
        letter-spacing: 0.03em;
        color: #dbeafe;
    }}
    .toolbar .buttons {{
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
    }}
    .toolbar button {{
        border: 1px solid rgba(148, 163, 184, 0.22);
        background: rgba(15, 27, 45, 0.96);
        color: #e5eefc;
        border-radius: 999px;
        padding: 0.45rem 0.8rem;
        cursor: pointer;
        font-size: 0.82rem;
    }}
    .toolbar button:hover {{
        background: rgba(30, 41, 59, 1);
    }}
    .canvas-wrap {{
        position: relative;
        width: 100%;
        height: calc(100% - 58px);
        min-height: {height}px;
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 18px;
        overflow: hidden;
        background:
            radial-gradient(circle at top left, rgba(56, 189, 248, 0.08), transparent 25%),
            linear-gradient(180deg, rgba(8, 15, 28, 0.98), rgba(10, 16, 29, 0.98));
    }}
    #diagram {{
        width: 100%;
        height: 100%;
    }}
    .mermaid {{
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: visible;
    }}
    .mermaid svg {{
        width: 100% !important;
        height: auto !important;
        max-width: none !important;
    }}
    .hint {{
        font-size: 0.76rem;
        color: #94a3b8;
    }}
</style>
<div class="viewer">
    <div class="toolbar">
        <div>
            <div class="title">{title}</div>
            <div class="hint">Pan by dragging the canvas. Use the buttons or mouse wheel to zoom.</div>
        </div>
        <div class="buttons">
            <button id="zoomIn" type="button">Zoom in</button>
            <button id="zoomOut" type="button">Zoom out</button>
            <button id="fit" type="button">Fit</button>
            <button id="reset" type="button">Reset</button>
        </div>
    </div>
    <div class="canvas-wrap">
        <div id="diagram" class="mermaid">{markup}</div>
    </div>
</div>
<script type="module">
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';

mermaid.initialize({{ startOnLoad: true, securityLevel: 'loose', theme: 'dark' }});
</script>
<script src="https://cdn.jsdelivr.net/npm/svg-pan-zoom@3.6.1/dist/svg-pan-zoom.min.js"></script>
<script>
window.svgPanZoom = window.svgPanZoom || svgPanZoom;
</script>
<script>
const diagram = document.getElementById('diagram');
const zoomInButton = document.getElementById('zoomIn');
const zoomOutButton = document.getElementById('zoomOut');
const fitButton = document.getElementById('fit');
const resetButton = document.getElementById('reset');

let panZoom = null;

function attachPanZoom() {{
    const svg = diagram.querySelector('svg');
    if (!svg) {{
        window.requestAnimationFrame(attachPanZoom);
        return;
    }}

    if (panZoom) {{
        panZoom.destroy();
    }}

    svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
    svg.style.width = '100%';
    svg.style.height = '100%';

    panZoom = window.svgPanZoom(svg, {{
        zoomEnabled: true,
        panEnabled: true,
        controlIconsEnabled: false,
        fit: true,
        center: true,
        minZoom: 0.15,
        maxZoom: 8,
        zoomScaleSensitivity: 0.2,
        dblClickZoomEnabled: true,
        mouseWheelZoomEnabled: true,
    }});

    zoomInButton.onclick = () => panZoom.zoomIn();
    zoomOutButton.onclick = () => panZoom.zoomOut();
    fitButton.onclick = () => {{ panZoom.fit(); panZoom.center(); }};
    resetButton.onclick = () => {{ panZoom.resetZoom(); panZoom.center(); }};
}}

window.addEventListener('load', () => window.requestAnimationFrame(attachPanZoom));
window.addEventListener('resize', () => {{ if (panZoom) {{ panZoom.resize(); panZoom.fit(); panZoom.center(); }} }});
</script>
"""