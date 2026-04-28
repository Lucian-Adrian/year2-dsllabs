from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Iterable, TypeVar

EPSILON = "ε"
ARROWS = ("->", "→", "")
T = TypeVar("T")


def _dedupe_preserve_order(items: Iterable[T]) -> tuple[T, ...]:
    seen: set[T] = set()
    ordered: list[T] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return tuple(ordered)


def _format_rhs(rhs: tuple[str, ...]) -> str:
    return EPSILON if not rhs else " ".join(rhs)


def tokenize_symbol_sequence(raw: str) -> tuple[str, ...]:
    value = raw.strip()
    if not value or value == EPSILON:
        return ()
    if " " in value:
        return tuple(token for token in value.split() if token and token != EPSILON)
    return tuple(value)


def _infer_non_terminal(token: str) -> bool:
    return bool(token) and token[0].isupper()


@dataclass(frozen=True, order=True)
class Production:
    lhs: str
    rhs: tuple[str, ...] = field(default_factory=tuple)

    def __str__(self) -> str:
        return f"{self.lhs} → {_format_rhs(self.rhs)}"

    def __repr__(self) -> str:
        return str(self)


@dataclass(frozen=True)
class Grammar:
    non_terminals: frozenset[str]
    terminals: frozenset[str]
    start_symbol: str
    productions: tuple[Production, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.non_terminals & self.terminals:
            overlap = ", ".join(sorted(self.non_terminals & self.terminals))
            raise ValueError(f"Grammar symbols overlap: {overlap}")
        if self.start_symbol not in self.non_terminals:
            raise ValueError(f"Start symbol {self.start_symbol!r} is not a non-terminal")
        for production in self.productions:
            if production.lhs not in self.non_terminals:
                raise ValueError(f"Unknown non-terminal on LHS: {production.lhs!r}")
            for token in production.rhs:
                if token not in self.non_terminals and token not in self.terminals:
                    raise ValueError(f"Unknown symbol in RHS: {token!r}")

    @classmethod
    def from_variant_record(cls, record: dict[str, Any]) -> "Grammar":
        productions = tuple(
            Production(item["lhs"], tokenize_symbol_sequence(item["rhs"]))
            for item in record["productions"]
        )
        non_terminals = set(record["non_terminals"])
        terminals = set(record["terminals"])
        for production in productions:
            non_terminals.add(production.lhs)
            for token in production.rhs:
                if _infer_non_terminal(token):
                    non_terminals.add(token)
                else:
                    terminals.add(token)
        terminals.difference_update(non_terminals)
        return cls(
            non_terminals=frozenset(non_terminals),
            terminals=frozenset(terminals),
            start_symbol=record["start"],
            productions=_dedupe_preserve_order(productions),
        )

    @classmethod
    def from_json_dict(cls, data: dict[str, Any]) -> "Grammar":
        if "variant" in data and "productions" in data:
            return cls.from_variant_record(data)

        productions = tuple(
            Production(item[0], tokenize_symbol_sequence(item[1]))
            for item in data["productions"]
        )
        return cls(
            non_terminals=frozenset(data["non_terminals"]),
            terminals=frozenset(data["terminals"]),
            start_symbol=data.get("start", data.get("start_symbol", "S")),
            productions=_dedupe_preserve_order(productions),
        )

    @classmethod
    def from_text(cls, text: str) -> "Grammar":
        productions: list[Production] = []
        lhs_candidates: list[str] = []

        for raw_line in text.splitlines():
            line = raw_line.split("#", 1)[0].split("//", 1)[0].strip()
            if not line:
                continue

            arrow = next((candidate for candidate in ARROWS if candidate in line), None)
            if arrow is None:
                continue

            lhs_raw, rhs_raw = line.split(arrow, 1)
            lhs = lhs_raw.strip().split()[0]
            lhs_candidates.append(lhs)

            for alternative in rhs_raw.split("|"):
                productions.append(Production(lhs, tokenize_symbol_sequence(alternative)))

        if not productions:
            raise ValueError("No productions found in grammar text")

        non_terminals = set(lhs_candidates)
        for production in productions:
            for token in production.rhs:
                if _infer_non_terminal(token):
                    non_terminals.add(token)

        terminals = {
            token
            for production in productions
            for token in production.rhs
            if token not in non_terminals
        }
        start_symbol = lhs_candidates[0]
        return cls(
            non_terminals=frozenset(non_terminals),
            terminals=frozenset(terminals),
            start_symbol=start_symbol,
            productions=_dedupe_preserve_order(productions),
        )

    @classmethod
    def from_file(cls, path: str | Path) -> "Grammar":
        file_path = Path(path)
        if file_path.suffix.lower() == ".json":
            import json

            return cls.from_json_dict(json.loads(file_path.read_text(encoding="utf-8")))
        return cls.from_text(file_path.read_text(encoding="utf-8"))

    @property
    def symbols(self) -> set[str]:
        return set(self.non_terminals) | set(self.terminals)

    def with_updates(
        self,
        *,
        non_terminals: Iterable[str] | None = None,
        terminals: Iterable[str] | None = None,
        start_symbol: str | None = None,
        productions: Iterable[Production] | None = None,
    ) -> "Grammar":
        return replace(
            self,
            non_terminals=frozenset(non_terminals) if non_terminals is not None else self.non_terminals,
            terminals=frozenset(terminals) if terminals is not None else self.terminals,
            start_symbol=start_symbol if start_symbol is not None else self.start_symbol,
            productions=_dedupe_preserve_order(productions) if productions is not None else self.productions,
        )

    def production_groups(self) -> dict[str, tuple[Production, ...]]:
        groups: dict[str, list[Production]] = {}
        for production in self.productions:
            groups.setdefault(production.lhs, []).append(production)
        return {lhs: tuple(items) for lhs, items in groups.items()}

    def symbols_in_rhs(self) -> set[str]:
        return {token for production in self.productions for token in production.rhs}

    def production_count(self) -> int:
        return len(self.productions)

    def nullable_productions(self) -> int:
        return sum(1 for production in self.productions if not production.rhs)

    def pretty(self) -> str:
        lines = [
            f"G = (VN, VT, P, {self.start_symbol})",
            f"VN = {{{', '.join(sorted(self.non_terminals))}}}",
            f"VT = {{{', '.join(sorted(self.terminals))}}}",
            "P = {",
        ]
        for production in self.productions:
            lines.append(f"  {production.lhs} → {_format_rhs(production.rhs)}")
        lines.append("}")
        return "\n".join(lines)

    def cnf_issues(self) -> list[str]:
        issues: list[str] = []
        start_on_rhs = self.start_symbol in self.symbols_in_rhs()
        for production in self.productions:
            if production.lhs not in self.non_terminals:
                issues.append(f"LHS {production.lhs!r} is not a non-terminal")
                continue

            rhs = production.rhs
            if not rhs:
                if production.lhs != self.start_symbol:
                    issues.append(f"{production} is ε but the left-hand side is not the start symbol")
                elif start_on_rhs:
                    issues.append(
                        f"{production} is allowed only when the start symbol does not appear on the right-hand side"
                    )
                continue

            if len(rhs) == 1:
                if rhs[0] not in self.terminals:
                    issues.append(f"{production} is unary but does not produce a terminal")
                continue

            if len(rhs) == 2:
                if not all(symbol in self.non_terminals for symbol in rhs):
                    issues.append(f"{production} is binary but contains a terminal")
                continue

            issues.append(f"{production} is longer than 2 symbols")

        return issues

    def is_cnf(self) -> bool:
        return not self.cnf_issues()

    def summary(self) -> dict[str, Any]:
        return {
            "non_terminals": len(self.non_terminals),
            "terminals": len(self.terminals),
            "productions": len(self.productions),
            "nullable": self.nullable_productions(),
            "start_symbol": self.start_symbol,
        }