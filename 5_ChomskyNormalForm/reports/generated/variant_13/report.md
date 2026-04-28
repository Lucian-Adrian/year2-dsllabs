# Variant 13

## Overview

- Start symbol: `S`
- Original productions: 10
- Final productions: 23
- Helper symbols introduced: 8
- Nullable symbols detected: 1
- CNF check: passed

## Pipeline

```mermaid
flowchart LR
    classDef stage fill:#0f172a,stroke:#38bdf8,color:#e2e8f0,stroke-width:1px;
    classDef success fill:#052e1a,stroke:#22c55e,color:#dcfce7,stroke-width:1px;
    S0["Original<br/>10 productions"]
    S1["Augment start symbol<br/>11 productions"]
    S2["Eliminate ε-productions<br/>13 productions"]
    S3["Eliminate unit productions<br/>22 productions"]
    S4["Remove useless symbols<br/>15 productions"]
    S5["Isolate terminals<br/>17 productions"]
    S6["Binarize long productions<br/>23 productions"]
    S7["Final cleanup<br/>23 productions"]
    S0 --> S1
    S1 --> S2
    S2 --> S3
    S3 --> S4
    S4 --> S5
    S5 --> S6
    S6 --> S7
    class S7 success;
    class S0 stage;
    class S1 stage;
    class S2 stage;
    class S3 stage;
    class S4 stage;
    class S5 stage;
    class S6 stage;
```

## Original Grammar

```text
G = (VN, VT, P, S)
VN = {A, B, C, D, S}
VT = {a, b}
P = {
  S → a B
  S → D A
  A → a
  A → B D
  A → b D A B
  B → b
  B → B A
  D → ε
  D → B A
  C → B A
}
```

## Final CNF

```text
G = (VN, VT, P, S0)
VN = {A, B, D, H1, H2, H3, H4, H5, H6, S0, T_a, T_b}
VT = {a, b}
P = {
  T_b → b
  T_a → a
  D → B A
  B → b
  B → B A
  A → a
  A → B D
  A → T_b H1
  H1 → A B
  A → T_b H2
  H2 → D H3
  H3 → A B
  A → b
  A → B A
  S0 → a
  S0 → B D
  S0 → T_b H4
  H4 → A B
  S0 → T_b H5
  H5 → D H6
  H6 → A B
  S0 → T_a B
  S0 → D A
}
```

## Step Summary

### Augment start symbol

Introduce a fresh start symbol so ε handling stays standard and the original start can be normalized safely.

- Notes:
  - New start symbol: S0

- Added:
  - S0 → S

### Eliminate ε-productions

Generate nullable variants and remove empty productions everywhere except the fresh start symbol.

- Notes:
  - Nullable symbols: D

- Added:
  - S → A
  - A → B
  - A → b A B
- Removed:
  - D → ε

### Eliminate unit productions

Replace renaming chains with the non-unit productions they reach.

- Notes:
  - A -> {A, B}
  - B -> {B}
  - C -> {C}
  - D -> {D}
  - S -> {A, S}
  - S0 -> {A, S, S0}

- Added:
  - S → a
  - S → B D
  - S → b A B
  - S → b D A B
  - A → b
  - A → B A
  - S0 → a
  - S0 → B D
  - ... +4 more
- Removed:
  - S0 → S
  - S → A
  - A → B

### Remove useless symbols

Remove non-productive and inaccessible symbols so the grammar is minimal before the CNF rewrite stage.

- Notes:
  - Productive symbols: A, B, C, D, S, S0
  - Reachable symbols: A, B, D, S0

- Removed:
  - S → a
  - S → B D
  - S → b A B
  - S → b D A B
  - S → a B
  - S → D A
  - C → B A

### Isolate terminals

Replace terminals that appear inside long productions with fresh pre-terminal symbols.

- Notes:
  - a -> T_a
  - b -> T_b

- Added:
  - T_b → b
  - T_a → a
  - A → T_b A B
  - A → T_b D A B
  - S0 → T_b A B
  - S0 → T_b D A B
  - S0 → T_a B
- Removed:
  - A → b A B
  - A → b D A B
  - S0 → b A B
  - S0 → b D A B
  - S0 → a B

### Binarize long productions

Break productions longer than two symbols into a chain of binary rules.

- Notes:
  - Helpers introduced: H1, H2, H3, H4, H5, H6

- Added:
  - A → T_b H1
  - H1 → A B
  - A → T_b H2
  - H2 → D H3
  - H3 → A B
  - S0 → T_b H4
  - H4 → A B
  - S0 → T_b H5
  - ... +2 more
- Removed:
  - A → T_b A B
  - A → T_b D A B
  - S0 → T_b A B
  - S0 → T_b D A B

### Final cleanup

Remove non-productive and inaccessible symbols so the grammar is minimal before the CNF rewrite stage.

- Notes:
  - Productive symbols: A, B, D, H1, H2, H3, H4, H5, H6, S0, T_a, T_b
  - Reachable symbols: A, B, D, H1, H2, H3, H4, H5, H6, S0, T_a, T_b


## Validation

The final grammar satisfies Chomsky Normal Form.
