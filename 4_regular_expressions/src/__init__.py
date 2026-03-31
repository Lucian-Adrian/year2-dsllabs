"""Lab 4 regular expression toolkit."""

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
    "generate_language",
    "generate_random_word",
    "generation_trace_to_mermaid",
    "normalize_expression",
    "parse_regex",
    "regex_pipeline_mermaid",
    "to_python_regex",
]
