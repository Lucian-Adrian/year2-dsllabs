from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from itertools import combinations
from typing import Any, Iterable

from .grammar import Grammar, Production


def _dedupe_preserve_order(items: Iterable[Production]) -> tuple[Production, ...]:
    seen: set[Production] = set()
    ordered: list[Production] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return tuple(ordered)


def _group_by_lhs(grammar: Grammar) -> dict[str, tuple[Production, ...]]:
    groups: dict[str, list[Production]] = defaultdict(list)
    for production in grammar.productions:
        groups[production.lhs].append(production)
    return {lhs: tuple(items) for lhs, items in groups.items()}


def _format_production_list(productions: Iterable[Production], limit: int = 8) -> tuple[str, ...]:
    items = list(productions)
    preview = [str(item) for item in items[:limit]]
    if len(items) > limit:
        preview.append(f"... +{len(items) - limit} more")
    return tuple(preview)


def _diff_productions(before: Grammar, after: Grammar) -> tuple[tuple[Production, ...], tuple[Production, ...]]:
    before_set = set(before.productions)
    after_set = set(after.productions)
    removed = tuple(prod for prod in before.productions if prod not in after_set)
    added = tuple(prod for prod in after.productions if prod not in before_set)
    return added, removed


def _nullable_symbols(grammar: Grammar) -> set[str]:
    nullable: set[str] = set()
    changed = True
    grouped = _group_by_lhs(grammar)
    while changed:
        changed = False
        for lhs, productions in grouped.items():
            if lhs in nullable:
                continue
            for production in productions:
                if not production.rhs:
                    nullable.add(lhs)
                    changed = True
                    break
                if all(symbol in nullable for symbol in production.rhs):
                    nullable.add(lhs)
                    changed = True
                    break
    return nullable


def _unit_closure(grammar: Grammar) -> dict[str, set[str]]:
    grouped = _group_by_lhs(grammar)
    closure: dict[str, set[str]] = {nt: {nt} for nt in grammar.non_terminals}
    changed = True

    while changed:
        changed = False
        for lhs in grammar.non_terminals:
            reachable = closure[lhs]
            for production in grouped.get(lhs, ()):  # type: ignore[arg-type]
                if len(production.rhs) != 1:
                    continue
                target = production.rhs[0]
                if target not in grammar.non_terminals or target in reachable:
                    continue
                new_targets = closure[target] - reachable
                if not new_targets:
                    continue
                reachable.update(new_targets)
                changed = True

    return closure


def _productive_symbols(grammar: Grammar) -> set[str]:
    productive: set[str] = set()
    changed = True
    grouped = _group_by_lhs(grammar)
    while changed:
        changed = False
        for lhs, productions in grouped.items():
            if lhs in productive:
                continue
            for production in productions:
                if all(symbol in grammar.terminals or symbol in productive for symbol in production.rhs):
                    productive.add(lhs)
                    changed = True
                    break
    return productive


def _reachable_symbols(grammar: Grammar) -> set[str]:
    reachable = {grammar.start_symbol}
    grouped = _group_by_lhs(grammar)
    queue = deque([grammar.start_symbol])
    while queue:
        lhs = queue.popleft()
        for production in grouped.get(lhs, ()):  # type: ignore[arg-type]
            for symbol in production.rhs:
                if symbol in grammar.non_terminals and symbol not in reachable:
                    reachable.add(symbol)
                    queue.append(symbol)
    return reachable


def _fresh_name(used: set[str], base: str) -> str:
    if base not in used:
        used.add(base)
        return base
    index = 2
    while True:
        candidate = f"{base}_{index}"
        if candidate not in used:
            used.add(candidate)
            return candidate
        index += 1


@dataclass(frozen=True)
class CNFStep:
    title: str
    description: str
    before: Grammar
    after: Grammar
    added: tuple[Production, ...] = ()
    removed: tuple[Production, ...] = ()
    notes: tuple[str, ...] = ()

    def preview(self, limit: int = 8) -> dict[str, tuple[str, ...]]:
        return {
            "added": _format_production_list(self.added, limit=limit),
            "removed": _format_production_list(self.removed, limit=limit),
        }


@dataclass(frozen=True)
class CNFConversionResult:
    original: Grammar
    final: Grammar
    steps: tuple[CNFStep, ...]
    helper_symbols: tuple[str, ...]
    nullable_symbols: tuple[str, ...]
    unit_closure: dict[str, tuple[str, ...]]
    issues: tuple[str, ...]

    def is_valid(self) -> bool:
        return not self.issues

    def step_titles(self) -> tuple[str, ...]:
        return tuple(step.title for step in self.steps)

    def summary(self) -> dict[str, Any]:
        return {
            "original_productions": self.original.production_count(),
            "final_productions": self.final.production_count(),
            "steps": len(self.steps),
            "helpers": len(self.helper_symbols),
            "nullable_symbols": len(self.nullable_symbols),
            "is_cnf": self.is_valid(),
        }


class SymbolFactory:
    def __init__(self, used_symbols: Iterable[str]):
        self._used = set(used_symbols)
        self._helper_index = 1

    def fresh(self, base: str) -> str:
        return _fresh_name(self._used, base)

    def helper(self, prefix: str = "H") -> str:
        while True:
            candidate = f"{prefix}{self._helper_index}"
            self._helper_index += 1
            if candidate not in self._used:
                self._used.add(candidate)
                return candidate

    def terminal_alias(self, terminal: str) -> str:
        return self.fresh(f"T_{terminal}")


class CNFConverter:
    def convert(self, grammar: Grammar) -> CNFConversionResult:
        steps: list[CNFStep] = []
        helper_symbols: list[str] = []

        working, step = self._augment_start(grammar)
        steps.append(step)

        factory = SymbolFactory(working.symbols)

        working, step = self._eliminate_epsilon(working)
        steps.append(step)

        working, step = self._eliminate_unit_productions(working)
        steps.append(step)

        working, step = self._remove_useless_symbols(working, title="Remove useless symbols")
        steps.append(step)

        working, step, aliases = self._isolate_terminals(working, factory)
        helper_symbols.extend(aliases)
        steps.append(step)

        working, step, helpers = self._binarize(working, factory)
        helper_symbols.extend(helpers)
        steps.append(step)

        working, step = self._remove_useless_symbols(working, title="Final cleanup")
        steps.append(step)

        issues = tuple(working.cnf_issues())
        unit_map = {lhs: tuple(sorted(targets)) for lhs, targets in _unit_closure(working).items()}
        nullable = tuple(sorted(_nullable_symbols(grammar)))

        return CNFConversionResult(
            original=grammar,
            final=working,
            steps=tuple(steps),
            helper_symbols=tuple(dict.fromkeys(helper_symbols)),
            nullable_symbols=nullable,
            unit_closure=unit_map,
            issues=issues,
        )

    def _augment_start(self, grammar: Grammar) -> tuple[Grammar, CNFStep]:
        factory = SymbolFactory(grammar.symbols)
        new_start = factory.fresh("S0")
        augmented = grammar.with_updates(
            non_terminals=set(grammar.non_terminals) | {new_start},
            productions=(Production(new_start, (grammar.start_symbol,)),) + grammar.productions,
            start_symbol=new_start,
        )
        step = CNFStep(
            title="Augment start symbol",
            description="Introduce a fresh start symbol so ε handling stays standard and the original start can be normalized safely.",
            before=grammar,
            after=augmented,
            added=(Production(new_start, (grammar.start_symbol,)),),
            notes=(f"New start symbol: {new_start}",),
        )
        return augmented, step

    def _eliminate_epsilon(self, grammar: Grammar) -> tuple[Grammar, CNFStep]:
        nullable = _nullable_symbols(grammar)
        new_productions: list[Production] = []

        for production in grammar.productions:
            if not production.rhs:
                if production.lhs == grammar.start_symbol:
                    new_productions.append(production)
                continue

            nullable_positions = [index for index, symbol in enumerate(production.rhs) if symbol in nullable]
            variants = {production.rhs}

            for count in range(1, len(nullable_positions) + 1):
                for combo in combinations(nullable_positions, count):
                    rhs = tuple(
                        symbol
                        for index, symbol in enumerate(production.rhs)
                        if index not in combo
                    )
                    if rhs or production.lhs == grammar.start_symbol:
                        variants.add(rhs)

            for rhs in variants:
                if rhs:
                    new_productions.append(Production(production.lhs, rhs))
                elif production.lhs == grammar.start_symbol:
                    new_productions.append(Production(production.lhs, rhs))

        after = grammar.with_updates(productions=new_productions)
        added, removed = _diff_productions(grammar, after)
        step = CNFStep(
            title="Eliminate ε-productions",
            description="Generate nullable variants and remove empty productions everywhere except the fresh start symbol.",
            before=grammar,
            after=after,
            added=added,
            removed=removed,
            notes=(f"Nullable symbols: {', '.join(sorted(nullable)) if nullable else 'none'}",),
        )
        return after, step

    def _eliminate_unit_productions(self, grammar: Grammar) -> tuple[Grammar, CNFStep]:
        closure = _unit_closure(grammar)
        grouped = _group_by_lhs(grammar)
        new_productions: list[Production] = []

        for lhs, reachable in closure.items():
            for target in sorted(reachable):
                for production in grouped.get(target, ()):  # type: ignore[arg-type]
                    if len(production.rhs) == 1 and production.rhs[0] in grammar.non_terminals:
                        continue
                    new_productions.append(Production(lhs, production.rhs))

        after = grammar.with_updates(productions=new_productions)
        added, removed = _diff_productions(grammar, after)
        closure_notes = tuple(
            f"{lhs} -> {{{', '.join(sorted(targets))}}}" for lhs, targets in sorted(closure.items())
        )
        step = CNFStep(
            title="Eliminate unit productions",
            description="Replace renaming chains with the non-unit productions they reach.",
            before=grammar,
            after=after,
            added=added,
            removed=removed,
            notes=closure_notes,
        )
        return after, step

    def _remove_useless_symbols(self, grammar: Grammar, *, title: str) -> tuple[Grammar, CNFStep]:
        productive = _productive_symbols(grammar)
        productive.add(grammar.start_symbol)
        productive_productions = [
            production
            for production in grammar.productions
            if production.lhs in productive
            and all(symbol in grammar.terminals or symbol in productive for symbol in production.rhs)
        ]
        productive_grammar = grammar.with_updates(
            non_terminals=productive,
            productions=productive_productions,
        )

        reachable = _reachable_symbols(productive_grammar)
        reachable_productions = [
            production
            for production in productive_grammar.productions
            if production.lhs in reachable
            and all(symbol in productive_grammar.terminals or symbol in reachable for symbol in production.rhs)
        ]
        after = productive_grammar.with_updates(
            non_terminals=reachable,
            productions=reachable_productions,
        )

        added, removed = _diff_productions(grammar, after)
        step = CNFStep(
            title=title,
            description="Remove non-productive and inaccessible symbols so the grammar is minimal before the CNF rewrite stage.",
            before=grammar,
            after=after,
            added=added,
            removed=removed,
            notes=(
                f"Productive symbols: {', '.join(sorted(productive)) if productive else 'none'}",
                f"Reachable symbols: {', '.join(sorted(reachable)) if reachable else 'none'}",
            ),
        )
        return after, step

    def _isolate_terminals(
        self,
        grammar: Grammar,
        factory: SymbolFactory,
    ) -> tuple[Grammar, CNFStep, tuple[str, ...]]:
        terminal_aliases: dict[str, str] = {}
        alias_productions: list[Production] = []
        rewritten: list[Production] = []

        for production in grammar.productions:
            if len(production.rhs) <= 1:
                rewritten.append(production)
                continue

            rhs: list[str] = []
            for symbol in production.rhs:
                if symbol in grammar.terminals:
                    alias = terminal_aliases.get(symbol)
                    if alias is None:
                        alias = factory.terminal_alias(symbol)
                        terminal_aliases[symbol] = alias
                        alias_productions.append(Production(alias, (symbol,)))
                    rhs.append(alias)
                else:
                    rhs.append(symbol)
            rewritten.append(Production(production.lhs, tuple(rhs)))

        after = grammar.with_updates(
            non_terminals=set(grammar.non_terminals) | set(terminal_aliases.values()),
            productions=alias_productions + rewritten,
        )
        added, removed = _diff_productions(grammar, after)
        notes = tuple(
            f"{terminal} -> {alias}" for terminal, alias in sorted(terminal_aliases.items())
        ) or ("No terminal isolation was needed.",)
        step = CNFStep(
            title="Isolate terminals",
            description="Replace terminals that appear inside long productions with fresh pre-terminal symbols.",
            before=grammar,
            after=after,
            added=added,
            removed=removed,
            notes=notes,
        )
        return after, step, tuple(terminal_aliases.values())

    def _binarize(
        self,
        grammar: Grammar,
        factory: SymbolFactory,
    ) -> tuple[Grammar, CNFStep, tuple[str, ...]]:
        new_productions: list[Production] = []
        helper_symbols: list[str] = []

        for production in grammar.productions:
            if len(production.rhs) <= 2:
                new_productions.append(production)
                continue

            symbols = list(production.rhs)
            head = production.lhs
            while len(symbols) > 2:
                helper = factory.helper("H")
                helper_symbols.append(helper)
                new_productions.append(Production(head, (symbols[0], helper)))
                head = helper
                symbols = symbols[1:]
            new_productions.append(Production(head, tuple(symbols)))

        after = grammar.with_updates(
            non_terminals=set(grammar.non_terminals) | set(helper_symbols),
            productions=new_productions,
        )
        added, removed = _diff_productions(grammar, after)
        step = CNFStep(
            title="Binarize long productions",
            description="Break productions longer than two symbols into a chain of binary rules.",
            before=grammar,
            after=after,
            added=added,
            removed=removed,
            notes=(f"Helpers introduced: {', '.join(helper_symbols) if helper_symbols else 'none'}",),
        )
        return after, step, tuple(helper_symbols)