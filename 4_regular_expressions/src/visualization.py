from __future__ import annotations

from typing import Any

from .ast_nodes import Alternation, Concat, Literal, RegexNode, Repeat
from .generator import GenerationStep


def _escape_mermaid_label(text: str) -> str:
    cleaned = text.replace('"', "'")
    return cleaned.replace("\n", " ").strip()


def _node_kind(node: RegexNode) -> str:
    if isinstance(node, Literal):
        return "literal"
    if isinstance(node, Alternation):
        return "alternation"
    if isinstance(node, Concat):
        return "concat"
    if isinstance(node, Repeat):
        return "repeat"
    return "unknown"


def _node_label(node: RegexNode) -> str:
    if isinstance(node, Literal):
        if node.value == "":
            return "Literal epsilon"
        return f"Literal {node.value}"

    if isinstance(node, Alternation):
        return f"Alternation {len(node.options)} options"

    if isinstance(node, Concat):
        return f"Concatenation {len(node.parts)} parts"

    if isinstance(node, Repeat):
        upper = "inf" if node.max_times is None else str(node.max_times)
        return f"Repeat {node.min_times}..{upper}"

    return "Node"


def ast_to_mermaid(node: RegexNode, *, title: str | None = None) -> str:
    """Builds a Mermaid flowchart representation of a regex AST."""

    lines: list[str] = []
    if title:
        lines.extend(["---", f'title: "{_escape_mermaid_label(title)}"', "---"])

    lines.extend(
        [
            "flowchart TD",
            "    classDef literal fill:#edf2ff,stroke:#3b5bdb,stroke-width:1px;",
            "    classDef concat fill:#f3faf7,stroke:#2f9e44,stroke-width:1px;",
            "    classDef alternation fill:#fff9db,stroke:#f08c00,stroke-width:1px;",
            "    classDef repeat fill:#fff0f6,stroke:#c2255c,stroke-width:1px;",
        ]
    )

    class_members: dict[str, list[str]] = {
        "literal": [],
        "concat": [],
        "alternation": [],
        "repeat": [],
    }

    next_id = 0

    def visit(current: RegexNode) -> str:
        nonlocal next_id
        node_id = f"N{next_id}"
        next_id += 1

        kind = _node_kind(current)
        label = _escape_mermaid_label(_node_label(current))
        lines.append(f'    {node_id}["{label}"]')
        if kind in class_members:
            class_members[kind].append(node_id)

        if isinstance(current, Concat):
            for idx, part in enumerate(current.parts, start=1):
                child = visit(part)
                lines.append(f"    {node_id} -->|part {idx}| {child}")

        elif isinstance(current, Alternation):
            for idx, option in enumerate(current.options, start=1):
                child = visit(option)
                lines.append(f"    {node_id} -->|option {idx}| {child}")

        elif isinstance(current, Repeat):
            child = visit(current.node)
            upper = "inf" if current.max_times is None else str(current.max_times)
            lines.append(f"    {node_id} -->|repeat {current.min_times}..{upper}| {child}")

        return node_id

    root = visit(node)
    lines.append(f"    ROOT([Regex Root]) --> {root}")

    for class_name, members in class_members.items():
        if members:
            lines.append(f"    class {','.join(members)} {class_name};")

    return "\n".join(lines) + "\n"


def regex_pipeline_mermaid() -> str:
    """High-level processing pipeline diagram for the lab workflow."""

    return "\n".join(
        [
            "flowchart LR",
            '    A[Input Regex] --> B[Normalization]',
            '    B --> C[Recursive-Descent Parser]',
            '    C --> D[AST Program]',
            '    D --> E[Bounded Generator]',
            '    E --> F[Candidate Words]',
            '    D --> G[Python Regex Compiler]',
            '    F --> H[Full-Match Validator]',
            '    G --> H',
            '    H --> I[Accepted Language Sample]',
            '    D --> J[Trace / Explainability]',
            '    J --> K[Mission Control Report]',
        ]
    ) + "\n"


def generation_trace_to_mermaid(word: str, steps: list[GenerationStep]) -> str:
    """Converts generation steps into a linear Mermaid flowchart."""

    lines = ["flowchart LR", '    S([Start]) --> T0["seeded decode"]']
    previous = "T0"

    for i, step in enumerate(steps, start=1):
        step_id = f"T{i}"
        detail = _escape_mermaid_label(step.detail)
        path = _escape_mermaid_label(step.path)
        label = _escape_mermaid_label(f"{i:02d} {step.action} | {path} | {detail}")
        lines.append(f'    {step_id}["{label}"]')
        lines.append(f"    {previous} --> {step_id}")
        previous = step_id

    final_label = _escape_mermaid_label(f"output: {word}")
    lines.append(f'    O(["{final_label}"])')
    lines.append(f"    {previous} --> O")
    return "\n".join(lines) + "\n"


def ast_metrics(node: RegexNode, *, max_repeat: int = 5) -> dict[str, Any]:
    """Computes structural metrics used in deeper explanatory reports."""

    def walk(current: RegexNode) -> tuple[int, int, int, int, int, int]:
        # Returns:
        # nodes, depth, alternations, repeats, literals, rough_paths
        if isinstance(current, Literal):
            return 1, 1, 0, 0, 1, 1

        if isinstance(current, Concat):
            child_stats = [walk(part) for part in current.parts]
            nodes = 1 + sum(s[0] for s in child_stats)
            depth = 1 + max((s[1] for s in child_stats), default=0)
            alternations = sum(s[2] for s in child_stats)
            repeats = sum(s[3] for s in child_stats)
            literals = sum(s[4] for s in child_stats)

            rough_paths = 1
            for stats in child_stats:
                rough_paths *= max(stats[5], 1)
                rough_paths = min(rough_paths, 1_000_000)

            return nodes, depth, alternations, repeats, literals, rough_paths

        if isinstance(current, Alternation):
            child_stats = [walk(option) for option in current.options]
            nodes = 1 + sum(s[0] for s in child_stats)
            depth = 1 + max((s[1] for s in child_stats), default=0)
            alternations = 1 + sum(s[2] for s in child_stats)
            repeats = sum(s[3] for s in child_stats)
            literals = sum(s[4] for s in child_stats)
            rough_paths = min(sum(s[5] for s in child_stats), 1_000_000)
            return nodes, depth, alternations, repeats, literals, rough_paths

        if isinstance(current, Repeat):
            inner = walk(current.node)
            upper = max_repeat if current.max_times is None else current.max_times
            upper = max(upper, current.min_times)

            rough_paths = 0
            for k in range(current.min_times, upper + 1):
                rough_paths += min(inner[5] ** k, 1_000_000)
                rough_paths = min(rough_paths, 1_000_000)

            return (
                1 + inner[0],
                1 + inner[1],
                inner[2],
                1 + inner[3],
                inner[4],
                rough_paths,
            )

        return 1, 1, 0, 0, 0, 1

    nodes, depth, alternations, repeats, literals, rough_paths = walk(node)
    return {
        "nodes": nodes,
        "depth": depth,
        "alternations": alternations,
        "repeats": repeats,
        "literals": literals,
        "rough_paths": rough_paths,
    }
