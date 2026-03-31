from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class VariantSpec:
    number: int
    expressions: tuple[str, str, str]


# These are interpreted from the official handwritten task images.
# Ambiguous numeric boundaries were disambiguated with explicit grouping
# so parser semantics remain faithful to shown examples.
VARIANTS: dict[int, VariantSpec] = {
    1: VariantSpec(
        number=1,
        expressions=(
            "(a|b)(c|d)E+G?",
            "P(Q|R|S)T(UV|W|X)*Z+",
            "1(0|1)*2(3|4)^5(3)(6)",
        ),
    ),
    2: VariantSpec(
        number=2,
        expressions=(
            "M?N^2(O|P)^3Q*R+",
            "(X|Y|Z)^3(8)+(9|0)",
            "(H|I)(J|K)L*N?",
        ),
    ),
    3: VariantSpec(
        number=3,
        expressions=(
            "O(P|Q|R)+2(3|4)",
            "A*B(C|D|E)F(G|H|I)^2",
            "J+K(L|M|N)*O?(P|Q)^3",
        ),
    ),
    4: VariantSpec(
        number=4,
        expressions=(
            "(S|T)(U|V)W*Y+24",
            "L(M|N)O^3P*Q(2|3)",
            "R*S(T|U|V)W(X|Y|Z)^2",
        ),
    ),
}


TASK_EXAMPLES: dict[int, tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]] = {
    1: (
        ("acEG", "bdE", "adEEG"),
        ("PQTUVUVZ", "PRTWWWWZ"),
        ("1023333336", "1124444436"),
    ),
    2: (
        ("MNNOOOQR", "NNPPPQQQRRR"),
        ("XXX89", "YYY88889"),
        ("HJLLN", "IKLLLLLL"),
    ),
    3: (
        ("OPP23", "OQQQQ24"),
        ("AAABCFGG", "AAAAAABDFHH"),
        ("JJKLOPPP", "JKNQQQ"),
    ),
    4: (
        ("SUWWY24", "SVWY24"),
        ("LMOOOPPPQ2", "LNOOOPQ3"),
        ("RSTWXX", "RRRSUWYY"),
    ),
}
