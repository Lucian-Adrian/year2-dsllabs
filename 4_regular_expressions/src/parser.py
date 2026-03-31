from __future__ import annotations

from dataclasses import dataclass

from .ast_nodes import Alternation, Concat, Literal, RegexNode, Repeat


class RegexSyntaxError(ValueError):
    """Raised when an input regular expression cannot be parsed."""


_SUPERSCRIPT_TO_DIGIT = {
    "\u2070": "0",
    "\u00b9": "1",
    "\u00b2": "2",
    "\u00b3": "3",
    "\u2074": "4",
    "\u2075": "5",
    "\u2076": "6",
    "\u2077": "7",
    "\u2078": "8",
    "\u2079": "9",
}


def normalize_expression(expression: str) -> str:
    """Normalizes expression text so parser handles handwritten notation.

    - Removes whitespace.
    - Converts Unicode superscripts to caret notation, e.g. A\u00b2 -> A^2.
    """
    output: list[str] = []
    previous_was_superscript = False

    for char in expression:
        if char.isspace():
            continue

        if char in _SUPERSCRIPT_TO_DIGIT:
            if not previous_was_superscript:
                output.append("^")
            output.append(_SUPERSCRIPT_TO_DIGIT[char])
            previous_was_superscript = True
            continue

        previous_was_superscript = False
        output.append(char)

    return "".join(output)


@dataclass
class _RegexParser:
    text: str
    index: int = 0

    def parse(self) -> RegexNode:
        node = self._parse_union()
        if self._peek() is not None:
            raise RegexSyntaxError(
                f"Unexpected token '{self._peek()}' at index {self.index}."
            )
        return node

    def _parse_union(self) -> RegexNode:
        options = [self._parse_concat()]

        while self._peek() == "|":
            self._consume("|")
            options.append(self._parse_concat())

        if len(options) == 1:
            return options[0]
        return Alternation(tuple(options))

    def _parse_concat(self) -> RegexNode:
        parts: list[RegexNode] = []

        while True:
            token = self._peek()
            if token is None or token in ")|":
                break
            parts.append(self._parse_repetition())

        if not parts:
            return Literal("")
        if len(parts) == 1:
            return parts[0]
        return Concat(tuple(parts))

    def _parse_repetition(self) -> RegexNode:
        node = self._parse_atom()
        seen_quantifier = False

        while True:
            token = self._peek()
            if token not in {"*", "+", "?", "^", "{"}:
                break
            if seen_quantifier:
                raise RegexSyntaxError(
                    "Nested repetition operators are not supported in this lab syntax."
                )

            seen_quantifier = True

            if token == "*":
                self._consume("*")
                node = Repeat(node=node, min_times=0, max_times=None)
                continue

            if token == "+":
                self._consume("+")
                node = Repeat(node=node, min_times=1, max_times=None)
                continue

            if token == "?":
                self._consume("?")
                node = Repeat(node=node, min_times=0, max_times=1)
                continue

            if token == "^":
                self._consume("^")
                amount = self._parse_number("Expected an integer after '^'.")
                node = Repeat(node=node, min_times=amount, max_times=amount)
                continue

            min_times, max_times = self._parse_braced_quantifier()
            node = Repeat(node=node, min_times=min_times, max_times=max_times)

        return node

    def _parse_braced_quantifier(self) -> tuple[int, int | None]:
        self._consume("{")

        if self._peek() == ",":
            min_times = 0
        else:
            min_times = self._parse_number("Expected minimum repetition in '{...}'.")

        if self._peek() == "}":
            self._consume("}")
            return min_times, min_times

        self._consume(",")

        if self._peek() == "}":
            self._consume("}")
            return min_times, None

        max_times = self._parse_number("Expected maximum repetition in '{m,n}'.")
        if max_times < min_times:
            raise RegexSyntaxError("Quantifier maximum cannot be smaller than minimum.")

        self._consume("}")
        return min_times, max_times

    def _parse_atom(self) -> RegexNode:
        token = self._peek()
        if token is None:
            raise RegexSyntaxError("Unexpected end of input while parsing atom.")

        if token == "(":
            self._consume("(")
            inner = self._parse_union()
            self._consume(")")
            return inner

        if token == "\\":
            self._consume("\\")
            escaped = self._peek()
            if escaped is None:
                raise RegexSyntaxError("Dangling escape at end of expression.")
            self._consume(escaped)
            return Literal(escaped)

        if token == "\u03b5":
            self._consume("\u03b5")
            return Literal("")

        if token in "*+?|)^{}":
            raise RegexSyntaxError(f"Unexpected token '{token}' at index {self.index}.")

        self._consume(token)
        return Literal(token)

    def _parse_number(self, message: str) -> int:
        start = self.index
        while (current := self._peek()) is not None and current.isdigit():
            self.index += 1

        if start == self.index:
            raise RegexSyntaxError(message)

        return int(self.text[start : self.index])

    def _peek(self) -> str | None:
        if self.index >= len(self.text):
            return None
        return self.text[self.index]

    def _consume(self, expected: str) -> None:
        current = self._peek()
        if current != expected:
            raise RegexSyntaxError(
                f"Expected '{expected}' at index {self.index}, found '{current}'."
            )
        self.index += 1


def parse_regex(expression: str) -> RegexNode:
    normalized = normalize_expression(expression)
    if not normalized:
        raise RegexSyntaxError("Expression is empty after normalization.")
    parser = _RegexParser(normalized)
    return parser.parse()
