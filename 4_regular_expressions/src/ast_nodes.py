from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union


@dataclass(frozen=True, slots=True)
class Literal:
    value: str


@dataclass(frozen=True, slots=True)
class Concat:
    parts: tuple["RegexNode", ...]


@dataclass(frozen=True, slots=True)
class Alternation:
    options: tuple["RegexNode", ...]


@dataclass(frozen=True, slots=True)
class Repeat:
    node: "RegexNode"
    min_times: int
    max_times: Optional[int]


RegexNode = Union[Literal, Concat, Alternation, Repeat]
