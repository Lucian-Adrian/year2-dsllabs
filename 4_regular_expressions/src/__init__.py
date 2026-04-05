"""Lab 4 regular expression toolkit."""

from .analysis import build_lab_analysis, render_terminal_transcript, write_analysis_bundle
from .generator import generate_language, generate_random_word, to_python_regex
from .parser import RegexSyntaxError, normalize_expression, parse_regex
from .variants import TASK_EXAMPLES, VARIANTS, VariantSpec
from .visualization import (
    ast_metrics,
    ast_to_mermaid,
    generation_trace_to_mermaid,
    regex_pipeline_mermaid,
)

__all__ = [
    "RegexSyntaxError",
    "TASK_EXAMPLES",
    "VARIANTS",
    "VariantSpec",
    "ast_metrics",
    "ast_to_mermaid",
    "build_lab_analysis",
    "generate_language",
    "generate_random_word",
    "generation_trace_to_mermaid",
    "normalize_expression",
    "parse_regex",
    "render_terminal_transcript",
    "regex_pipeline_mermaid",
    "to_python_regex",
    "write_analysis_bundle",
]
