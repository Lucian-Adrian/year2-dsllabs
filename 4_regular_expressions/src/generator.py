from __future__ import annotations

import random
import re
from dataclasses import dataclass
from typing import Iterable

from .ast_nodes import Alternation, Concat, Literal, RegexNode, Repeat
from .parser import parse_regex


@dataclass(frozen=True, slots=True)
class GenerationStep:
    path: str
    action: str
    detail: str


def _merge_unique(values: Iterable[str], limit: int) -> list[str]:
    unique: list[str] = []
    seen: set[str] = set()

    for item in values:
        if item in seen:
            continue
        seen.add(item)
        unique.append(item)
        if len(unique) >= limit:
            break

    return unique


def _concat_words(left: list[str], right: list[str], limit: int) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()

    for prefix in left:
        for suffix in right:
            candidate = prefix + suffix
            if candidate in seen:
                continue
            seen.add(candidate)
            merged.append(candidate)
            if len(merged) >= limit:
                return merged

    return merged


def _upper_repeat_bound(node: Repeat, max_repeat: int) -> int:
    if node.max_times is None:
        return max_repeat
    return node.max_times


def generate_language(
    node: RegexNode,
    *,
    max_repeat: int = 5,
    max_results: int = 200,
) -> list[str]:
    """Enumerates accepted words up to configurable limits.

    max_repeat is applied only to unbounded repetition operators (* and +).
    """

    if max_results <= 0:
        return []

    if isinstance(node, Literal):
        return [node.value]

    if isinstance(node, Alternation):
        words: list[str] = []
        for option in node.options:
            option_words = generate_language(
                option, max_repeat=max_repeat, max_results=max_results
            )
            words = _merge_unique([*words, *option_words], max_results)
            if len(words) >= max_results:
                break
        return words

    if isinstance(node, Concat):
        words = [""]
        for part in node.parts:
            part_words = generate_language(part, max_repeat=max_repeat, max_results=max_results)
            words = _concat_words(words, part_words, max_results)
            if not words:
                break
        return words

    if isinstance(node, Repeat):
        upper = _upper_repeat_bound(node, max_repeat)
        if upper < node.min_times:
            return []

        child_words = generate_language(
            node.node, max_repeat=max_repeat, max_results=max_results
        )
        words: list[str] = []

        for count in range(node.min_times, upper + 1):
            block = [""]
            for _ in range(count):
                block = _concat_words(block, child_words, max_results)
                if not block:
                    break
            words = _merge_unique([*words, *block], max_results)
            if len(words) >= max_results:
                break

        return words

    raise TypeError(f"Unsupported node type: {type(node)!r}")


def generate_random_word(
    node: RegexNode,
    *,
    max_repeat: int = 5,
    rng: random.Random | None = None,
    with_trace: bool = False,
) -> tuple[str, list[GenerationStep]]:
    """Generates one valid word and optionally returns expansion trace steps."""

    random_source = rng or random.Random()
    steps: list[GenerationStep] = []

    def sample(current: RegexNode, path: str) -> str:
        if isinstance(current, Literal):
            if with_trace:
                steps.append(GenerationStep(path, "literal", repr(current.value)))
            return current.value

        if isinstance(current, Alternation):
            index = random_source.randrange(len(current.options))
            if with_trace:
                steps.append(
                    GenerationStep(
                        path,
                        "choose-alternative",
                        f"option {index + 1} of {len(current.options)}",
                    )
                )
            return sample(current.options[index], f"{path}|{index}")

        if isinstance(current, Concat):
            if with_trace:
                steps.append(
                    GenerationStep(
                        path,
                        "concat",
                        f"{len(current.parts)} parts",
                    )
                )
            return "".join(sample(part, f"{path}.{i}") for i, part in enumerate(current.parts))

        if isinstance(current, Repeat):
            upper = _upper_repeat_bound(current, max_repeat)
            if upper < current.min_times:
                raise ValueError("Invalid repetition limits for random generation.")

            times = random_source.randint(current.min_times, upper)
            if with_trace:
                steps.append(
                    GenerationStep(
                        path,
                        "repeat",
                        f"{times} times (range {current.min_times}..{upper})",
                    )
                )
            return "".join(sample(current.node, f"{path}#{i}") for i in range(times))

        raise TypeError(f"Unsupported node type: {type(current)!r}")

    word = sample(node, "root")
    return word, steps


def to_python_regex(node: RegexNode) -> str:
    """Converts internal AST to a Python-compatible regex expression."""

    def emit(current: RegexNode) -> str:
        if isinstance(current, Literal):
            return re.escape(current.value)

        if isinstance(current, Concat):
            return "".join(emit(part) for part in current.parts)

        if isinstance(current, Alternation):
            content = "|".join(emit(option) for option in current.options)
            return f"(?:{content})"

        if isinstance(current, Repeat):
            inner = emit(current.node)
            wrapped = f"(?:{inner})"
            if current.min_times == 0 and current.max_times is None:
                return f"{wrapped}*"
            if current.min_times == 1 and current.max_times is None:
                return f"{wrapped}+"
            if current.min_times == 0 and current.max_times == 1:
                return f"{wrapped}?"
            if current.max_times is None:
                return f"{wrapped}{{{current.min_times},}}"
            if current.min_times == current.max_times:
                return f"{wrapped}{{{current.min_times}}}"
            return f"{wrapped}{{{current.min_times},{current.max_times}}}"

        raise TypeError(f"Unsupported node type: {type(current)!r}")

    return emit(node)


def explain_generation(
    expression: str,
    *,
    max_repeat: int = 5,
    seed: int = 42,
) -> tuple[str, list[GenerationStep]]:
    """Parses an expression and returns one generated word plus full expansion trace."""

    ast = parse_regex(expression)
    rng = random.Random(seed)
    return generate_random_word(ast, max_repeat=max_repeat, rng=rng, with_trace=True)
