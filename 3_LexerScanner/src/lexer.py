from __future__ import annotations

from dataclasses import dataclass
from typing import Generator, Iterable

from src.tokens import SourcePosition, SourceSpan, Token, TokenType

KEYWORDS = frozenset({"let", "def", "return"})
MATH_FUNCTIONS = frozenset(
    {
        "sin",
        "cos",
        "tan",
        "relu",
        "sigmoid",
        "softmax",
        "exp",
        "log",
    }
)


@dataclass(slots=True)
class LexerConfig:
    emit_comments: bool = True


@dataclass(slots=True)
class LexicalError(Exception):
    source_name: str
    source_text: str
    line: int
    column: int
    message: str
    offending_lexeme: str

    def __str__(self) -> str:
        return self.render()

    def render(self) -> str:
        lines = self.source_text.splitlines() or [""]
        snippet = lines[self.line - 1] if 0 < self.line <= len(lines) else ""
        caret = " " * (max(self.column, 1) - 1) + "^"
        return (
            f"Lexical Error at Line {self.line}, Column {self.column} in {self.source_name}:\n"
            f"{snippet}\n"
            f"{caret}\n"
            f"{self.message} Offending lexeme: {self.offending_lexeme!r}."
        )


class TensorScriptLexer:
    SIMPLE_TOKENS = {
        "=": TokenType.ASSIGN,
        ",": TokenType.COMMA,
        ";": TokenType.SEMICOLON,
        "(": TokenType.LEFT_PAREN,
        ")": TokenType.RIGHT_PAREN,
        "[": TokenType.LEFT_BRACKET,
        "]": TokenType.RIGHT_BRACKET,
        "+": TokenType.PLUS,
        "-": TokenType.MINUS,
        "*": TokenType.STAR,
        "/": TokenType.SLASH,
    }

    def __init__(
        self,
        source_text: str,
        source_name: str = "<memory>",
        config: LexerConfig | None = None,
    ) -> None:
        self.source_text = source_text
        self.source_name = source_name
        self.config = config or LexerConfig()
        self._index = 0
        self._line = 1
        self._column = 1

    def tokenize(self) -> Generator[Token, None, None]:
        while not self._is_at_end():
            current = self._peek()

            if current in " \t\r":
                self._advance()
                continue

            if current == "\n":
                self._advance()
                continue

            if current == "/" and self._peek(1) == "/":
                comment = self._scan_comment()
                if self.config.emit_comments:
                    yield comment
                continue

            if current.isalpha() or current == "_":
                yield self._scan_identifier_or_keyword()
                continue

            if current.isdigit() or (current == "." and self._peek(1).isdigit()):
                yield self._scan_number()
                continue

            token_type = self.SIMPLE_TOKENS.get(current)
            if token_type is not None:
                yield self._scan_simple_token(token_type)
                continue

            raise self._error("Unrecognized token.", current)

        yield self._make_token(
            TokenType.EOF, "", self._position(), self._position(), None
        )

    def collect(self) -> list[Token]:
        return list(self.tokenize())

    def _scan_comment(self) -> Token:
        start = self._position()
        lexeme_chars = [self._advance(), self._advance()]
        while not self._is_at_end() and self._peek() != "\n":
            lexeme_chars.append(self._advance())
        end = self._position()
        lexeme = "".join(lexeme_chars)
        return self._make_token(
            TokenType.COMMENT, lexeme, start, end, lexeme[2:].strip()
        )

    def _scan_identifier_or_keyword(self) -> Token:
        start = self._position()
        lexeme_chars: list[str] = []
        while not self._is_at_end() and (self._peek().isalnum() or self._peek() == "_"):
            lexeme_chars.append(self._advance())
        lexeme = "".join(lexeme_chars)
        end = self._position()

        if lexeme in KEYWORDS:
            token_type = TokenType.KEYWORD
        elif lexeme in MATH_FUNCTIONS:
            token_type = TokenType.MATH_FUNCTION
        else:
            token_type = TokenType.IDENTIFIER

        return self._make_token(token_type, lexeme, start, end, lexeme)

    def _scan_number(self) -> Token:
        start = self._position()
        lexeme_chars: list[str] = []
        dot_count = 0

        while not self._is_at_end():
            current = self._peek()
            if current.isdigit():
                lexeme_chars.append(self._advance())
                continue
            if current == ".":
                if dot_count == 1:
                    lexeme_preview = "".join(lexeme_chars) + current
                    raise self._error("Malformed numeric literal.", lexeme_preview)
                dot_count += 1
                lexeme_chars.append(self._advance())
                continue
            break

        lexeme = "".join(lexeme_chars)
        end = self._position()
        if lexeme in {"", "."}:
            raise self._error("Malformed numeric literal.", lexeme or self._peek())

        if dot_count == 1:
            token_type = TokenType.FLOAT
            value = float(lexeme)
        else:
            token_type = TokenType.INTEGER
            value = int(lexeme)
        return self._make_token(token_type, lexeme, start, end, value)

    def _scan_simple_token(self, token_type: TokenType) -> Token:
        start = self._position()
        lexeme = self._advance()
        end = self._position()
        return self._make_token(token_type, lexeme, start, end, lexeme)

    def _make_token(
        self,
        token_type: TokenType,
        lexeme: str,
        start: SourcePosition,
        end: SourcePosition,
        value: object,
    ) -> Token:
        return Token(
            token_type=token_type,
            lexeme=lexeme,
            span=SourceSpan(start=start, end=end),
            value=value,
        )

    def _is_at_end(self) -> bool:
        return self._index >= len(self.source_text)

    def _peek(self, offset: int = 0) -> str:
        position = self._index + offset
        if position >= len(self.source_text):
            return "\0"
        return self.source_text[position]

    def _advance(self) -> str:
        char = self.source_text[self._index]
        self._index += 1
        if char == "\n":
            self._line += 1
            self._column = 1
        else:
            self._column += 1
        return char

    def _position(self) -> SourcePosition:
        return SourcePosition(line=self._line, column=self._column, offset=self._index)

    def _error(self, message: str, offending_lexeme: str) -> LexicalError:
        return LexicalError(
            source_name=self.source_name,
            source_text=self.source_text,
            line=self._line,
            column=self._column,
            message=message,
            offending_lexeme=offending_lexeme,
        )


def iter_tokens(
    source_text: str, source_name: str = "<memory>", emit_comments: bool = True
) -> Iterable[Token]:
    lexer = TensorScriptLexer(
        source_text,
        source_name=source_name,
        config=LexerConfig(emit_comments=emit_comments),
    )
    return lexer.tokenize()
