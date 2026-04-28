from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from .grammar import Grammar

ROOT_DIR = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT_DIR / "config" / "variants.json"


@dataclass(frozen=True)
class VariantRecord:
    variant: int
    start: str
    non_terminals: tuple[str, ...]
    terminals: tuple[str, ...]
    productions: tuple[tuple[str, str], ...]

    @classmethod
    def from_dict(cls, variant_id: str, data: dict[str, Any]) -> "VariantRecord":
        return cls(
            variant=int(variant_id),
            start=data.get("start", "S"),
            non_terminals=tuple(data["non_terminals"]),
            terminals=tuple(data["terminals"]),
            productions=tuple((item["lhs"], item["rhs"]) for item in data["productions"]),
        )

    def to_grammar(self) -> Grammar:
        return Grammar.from_variant_record(
            {
                "variant": self.variant,
                "start": self.start,
                "non_terminals": list(self.non_terminals),
                "terminals": list(self.terminals),
                "productions": [{"lhs": lhs, "rhs": rhs} for lhs, rhs in self.productions],
            }
        )

    def production_count(self) -> int:
        return len(self.productions)

    def summary(self) -> dict[str, Any]:
        return {
            "variant": self.variant,
            "non_terminals": len(self.non_terminals),
            "terminals": len(self.terminals),
            "productions": len(self.productions),
            "start": self.start,
        }


@lru_cache(maxsize=1)
def load_variant_catalog() -> dict[int, VariantRecord]:
    payload = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    return {
        int(variant_id): VariantRecord.from_dict(variant_id, record)
        for variant_id, record in payload["variants"].items()
    }


def list_variants() -> list[int]:
    return sorted(load_variant_catalog())


def load_variant_record(variant_id: int) -> VariantRecord:
    catalog = load_variant_catalog()
    if variant_id not in catalog:
        raise KeyError(f"Unknown variant {variant_id}")
    return catalog[variant_id]


def load_variant_grammar(variant_id: int) -> Grammar:
    return load_variant_record(variant_id).to_grammar()


def all_variant_summaries() -> list[dict[str, Any]]:
    return [load_variant_record(variant_id).summary() for variant_id in list_variants()]