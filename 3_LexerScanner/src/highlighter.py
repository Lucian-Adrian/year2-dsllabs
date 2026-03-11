from __future__ import annotations

from rich.text import Text

from src.tokens import Token, TokenFamily, TokenType

STYLE_BY_FAMILY = {
    TokenFamily.DECLARATION: "bold bright_blue",
    TokenFamily.FUNCTION: "bold yellow",
    TokenFamily.NUMBER: "bold green",
    TokenFamily.COMMENT: "italic bright_black",
    TokenFamily.IDENTIFIER: "cyan",
    TokenFamily.SYMBOL: "magenta",
    TokenFamily.EOF: "dim",
}


def highlight_source(source_text: str, tokens: list[Token]) -> Text:
    highlighted = Text()
    cursor = 0

    for token in tokens:
        if token.token_type is TokenType.EOF:
            continue
        start = token.span.start.offset
        end = token.span.end.offset
        if cursor < start:
            highlighted.append(source_text[cursor:start])
        style = STYLE_BY_FAMILY.get(token.family, "white")
        highlighted.append(source_text[start:end], style=style)
        cursor = end

    if cursor < len(source_text):
        highlighted.append(source_text[cursor:])

    return highlighted
