# Mental Model — State-Space Compiler
## Pre-presentation reading. Know this cold.

---

## 1. The Chomsky Hierarchy

**One sentence:** A taxonomy of four grammar classes, each strictly more powerful than the last.

| Type | Name | Production Rule Shape | Machine Equivalent |
|---|---|---|---|
| 0 | Unrestricted | αAβ → γ (anything) | Turing Machine |
| 1 | Context-Sensitive | αAβ → αγβ, \|LHS\| ≤ \|RHS\| | Linear Bounded Automaton |
| 2 | Context-Free | A → γ (single NT on LHS) | Pushdown Automaton |
| **3** | **Regular** | **A → aB or A → a** | **Finite Automaton** |

**Why Type 3 is special:**
- Every rule has a single terminal up front and at most one non-terminal at the tail (right-linear).
- The "computation" has no memory — finite automaton, no stack, no tape.
- This means you can compile it into a lookup table. O(1) per character.
- **Variant 13 is Type 3.** The linter confirms this algebraically before any other step runs.

**The check in code:**

```python
# grammar.py
is_type3 = all(
    len(lhs) == 1 and lhs.isupper()       # single non-terminal
    and (
        re.match(r'^[a-z]$', rhs) or       # A → a
        re.match(r'^[a-z][A-Z]$', rhs) or  # A → aB (right-linear)
        rhs == ""                           # A → ε (terminator)
    )
    for lhs, rhs in productions
)
```

---

## 2. NDFA Uncertainty

**One sentence:** An NDFA's transition function maps (state, symbol) to a *set* of states — not one.

**The superposition model:**

When the NDFA reads symbol `a` at state `q1`, it doesn't choose a path:
```
q1 --a--> q1   (Branch A: stay at q1)
q1 --a--> q2   (Branch B: jump to q2)
```
Both branches are "alive" simultaneously. This is the non-determinism.

**Why you can't deploy this:**
- To simulate: you must track all active branches after every character.
- For a string of length `n`, worst case you track O(2^n) parallel states.
- A Python `re` engine running on production hardware has one instruction pointer.
- You can't branch the CPU. You need to pre-compile away the ambiguity.

**Variant 13 conflict locations:**
```
δ(q1, a) = {q1, q2}  ← Branch Point 1
δ(q2, a) = {q1, q2}  ← Branch Point 2
```

**The detector (src/ndfa.py):**
```python
def is_deterministic(self) -> bool:
    return all(len(targets) <= 1 for targets in self.transitions.values())
```
A DFA is the degenerate case where every frozenset has cardinality ≤ 1.

---

## 3. Powerset Construction (Subset Construction)

**One sentence:** Treat every *combination* of NDFA states as a single new DFA node, then BFS to find all reachable combinations.

**The key intuition:**

If the NDFA can be in states `{q1, q2}` at the same time, treat `{q1, q2}` as a *single* DFA state. It's a macro-state. The DFA never branches — it always knows exactly which macro-state it's in.

**BFS mechanics:**

```
1. Start with macro-state = frozenset({q0})
2. For each unprocessed macro-state M:
   For each symbol s in Σ:
       nxt = UNION of all δ(qi, s) for qi in M
       If nxt is new → add to queue
3. Repeat until queue is empty
```

**Why this terminates:** There are at most 2^|Q| possible subsets. Finite by definition.

**Variant 13 trace:**

```
Start:   {q0}
Read b:  δ(q0, b) = {q1}            → new macro-state {q1}
Read a:  δ(q1, a) = {q1, q2}        → new macro-state {q1, q2}  ← the union
Read b:  δ(q1,b)∪δ(q2,b) = {q3}    → new macro-state {q3} (accepting!)
No moves from {q3} → add ∅ (dead state)
```

**State count:**
- NDFA: 4 states (q0, q1, q2, q3)
- DFA: 5 macro-states ({q0}, {q1}, {q1,q2}, {q3}, ∅)
- Worst case: 2^4 = 16
- Pruned (unreachable): 11 macro-states never generated

**The dead state ∅:**
- Formal requirement: a DFA's transition function must be *total* — defined for every (state, symbol) pair.
- When {q3} reads `a` or `b`, there is no valid move. We route to ∅.
- ∅ loops to itself — it's a mathematical trap/sink.

---

## 4. Language of Variant 13

**One sentence:** Read the DFA's accepting paths backward to deduce what pattern it recognizes.

**DFA topology:**

```
{q0} --a--> {q0}           (loop: any number of a's)
{q0} --b--> {q1}           (first b — "committed")
{q1} --a--> {q1,q2}        (a's after first b)
{q1,q2} --a--> {q1,q2}    (loop: more a's)
{q1,q2} --b--> {q3} ✓     (second b → ACCEPT)
{q1} --b--> {q3} ✓         (second b directly → ACCEPT)
```

**Deduced language:**

```
L(M₁₃) = a* b a* b a*
```

- Zero or more `a`s
- Then exactly one `b`
- Then zero or more `a`s
- Then exactly one `b`
- Then zero or more `a`s

*(Simplified: strings over {a, b} that contain exactly two b's, in any position.)*

Actually more precisely: the grammar enforces that both b's must be reached through the specific path — let me be exact. The DFA accepts anything that eventually reaches {q3}. That requires exactly 2 b's at minimum (because you need one b to escape {q0} and another to reach {q3}). After {q3}, any `a` or `b` sends you to ∅ (dead). So:

```
L(M₁₃) = a* b a* b
```

**Strings confirmed:**

| Input | Path | Result |
|---|---|---|
| `ab` | {q0}→{q1}→{q3} | ACCEPT |
| `bab` | {q0}→{q1}→{q1,q2}→{q3} | ACCEPT |
| `abab` | {q0}→{q1}→{q1,q2}→{q1,q2}→{q3} | ...wait, actually {q0}→{q1}→{q1,q2}→{q3}→∅ = REJECT |

Let me re-trace `abab`:
```
a: {q0}→{q0}
b: {q0}→{q1}
a: {q1}→{q1,q2}
b: {q1,q2}→{q3}
```
Result: ACCEPT ✓

`ababb`:
```
a,b → {q1}
a   → {q1,q2}
b   → {q3}
b   → ∅ (dead)
```
Result: REJECT

So the pattern is: strings that end with the second `b` at the last position.
**Exact language: `a* b a* b`** — must end with `b`, exactly two `b`s total, any `a`s between and before.

---

## 5. Grammar Produced by DFA.to_grammar()

After compilation, the DFA's transition topology is read back out as formal grammar rules.

**Rule derivation logic:**
- Every edge `(qi, c) → qj` where qj is NOT dead → produces `qi → c qj`
- If `qj ∈ F` (accepting), also produce `qi → c` (terminal production)
- Every accepting state `qj` produces `qj → ε`

**Variant 13 DFA grammar output:**

```
{q0} → a {q0}
{q0} → b {q1}
{q1} → a {q1,q2}
{q1} → b {q3}
{q1} → b              ← because {q3} ∈ F
{q1,q2} → a {q1,q2}
{q1,q2} → b {q3}
{q1,q2} → b           ← because {q3} ∈ F
{q3} → ε
```

This is a valid **Type 3 Right-Linear Grammar** — confirms full round-trip: grammar classification → NDFA → DFA → grammar re-extraction.

---

## Quick-Reference Card

| Concept | One-liner |
|---|---|
| Chomsky Type 3 | `A → aB or A → a` only. Maps to finite automaton. |
| NDFA | δ returns a *set*. Superposition. Cannot deploy as-is. |
| Powerset Construction | Treat state-sets as nodes. BFS until stable. O(2^n) space, O(n) practice. |
| Dead state ∅ | Total function requirement. Trap/sink for undefined transitions. |
| Macro-state {q1,q2} | The union of two NDFA branches, collapsed into one DFA node. |
| L(V13) | `a* b a* b` — strings over {a,b} with exactly 2 b's, ends with b. |
| O(n) payoff | DFA execution is one lookup per character, no backtracking. |
