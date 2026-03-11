from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, unique
from typing import Any


@unique
class TokenType(Enum):
    KEYWORD = "KEYWORD"
    IDENTIFIER = "IDENTIFIER"
    MATH_FUNCTION = "MATH_FUNCTION"
    FLOAT = "FLOAT"
    INTEGER = "INTEGER"
    ASSIGN = "ASSIGN"
    COMMA = "COMMA"
    SEMICOLON = "SEMICOLON"
    LEFT_PAREN = "LEFT_PAREN"
    RIGHT_PAREN = "RIGHT_PAREN"
    LEFT_BRACKET = "LEFT_BRACKET"
    RIGHT_BRACKET = "RIGHT_BRACKET"
    PLUS = "PLUS"
    MINUS = "MINUS"
    STAR = "STAR"
    SLASH = "SLASH"
    COMMENT = "COMMENT"
    EOF = "EOF"

    @property
    def label(self) -> str:
        return self.value


@unique
class TokenFamily(Enum):
    DECLARATION = "DECLARATION"
    SYMBOL = "SYMBOL"
    NUMBER = "NUMBER"
    FUNCTION = "FUNCTION"
    COMMENT = "COMMENT"
    EOF = "EOF"
    IDENTIFIER = "IDENTIFIER"


@dataclass(frozen=True, slots=True)
class SourcePosition:
    line: int
    column: int
    offset: int


@dataclass(frozen=True, slots=True)
class SourceSpan:
    start: SourcePosition
    end: SourcePosition


@dataclass(frozen=True, slots=True)
class Token:
    token_type: TokenType
    lexeme: str
    span: SourceSpan
    value: Any = None

    @property
    def line(self) -> int:
        return self.span.start.line

    @property
    def column(self) -> int:
        return self.span.start.column

    @property
    def family(self) -> TokenFamily:
        if self.token_type is TokenType.KEYWORD:
            return TokenFamily.DECLARATION
        if self.token_type in {TokenType.FLOAT, TokenType.INTEGER}:
            return TokenFamily.NUMBER
        if self.token_type is TokenType.MATH_FUNCTION:
            return TokenFamily.FUNCTION
        if self.token_type is TokenType.COMMENT:
            return TokenFamily.COMMENT
        if self.token_type is TokenType.EOF:
            return TokenFamily.EOF
        if self.token_type is TokenType.IDENTIFIER:
            return TokenFamily.IDENTIFIER
        return TokenFamily.SYMBOL

    @property
    def memory_address(self) -> str:
        return hex(id(self))

    def to_row(self) -> tuple[str, str, str, str, str]:
        return (
            str(self.line),
            str(self.column),
            self.token_type.label,
            self.lexeme.replace("\n", "\\n"),
            self.memory_address,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "line": self.line,
            "column": self.column,
            "type": self.token_type.label,
            "family": self.family.value,
            "lexeme": self.lexeme,
            "value": self.value,
            "memory_address": self.memory_address,
            "start_offset": self.span.start.offset,
            "end_offset": self.span.end.offset,
        }
