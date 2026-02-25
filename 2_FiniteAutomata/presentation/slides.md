---
theme: default
colorSchema: dark
highlighter: shiki
lineNumbers: false
fonts:
  sans: 'Inter'
  mono: 'JetBrains Mono'
title: 'State-Space Compiler'
info: |
  Lab 2 — Formal Languages & Finite Automata
  Variant 13 · NDFA → DFA Powerset Compiler
transition: slide-left
drawings:
  persist: false
---

<style>
/* ── Global reset for dark presentation ── */
:root {
  --slidev-theme-primary: #3b82f6;
  --slidev-font-size: 1rem;
}

.slidev-layout {
  background: #0a0a0a;
  color: #ededed;
}

/* Mono labels */
.mono  { font-family: 'JetBrains Mono', monospace; font-size: 0.85em; }
.label {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.78em;
  font-weight: 600;
  letter-spacing: 0.04em;
}
.label-blue  { background: #1e3a5f; color: #93c5fd; border: 1px solid #2563eb; }
.label-green { background: #052e16; color: #86efac; border: 1px solid #16a34a; }
.label-red   { background: #450a0a; color: #fca5a5; border: 1px solid #dc2626; }
.label-amber { background: #431407; color: #fdba74; border: 1px solid #ea580c; }
.label-gray  { background: #1a1a1a; color: #a3a3a3; border: 1px solid #333; }

/* Module cards */
.module-card {
  background: #111;
  border: 1px solid #1f1f1f;
  border-radius: 8px;
  padding: 16px 20px;
  transition: border-color 0.2s;
}
.module-card:hover { border-color: #3b82f6; }
.module-card h3 { margin: 0 0 6px; font-size: 0.85rem; font-weight: 600; color: #ffffff; }
.module-card p  { margin: 0; font-size: 0.75rem; color: #555; line-height: 1.5; }

/* Stat blocks */
.stat-block {
  background: #0d0d0d;
  border: 1px solid #1f1f1f;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
}
.stat-block .num  { font-size: 2.4rem; font-weight: 700; letter-spacing: -0.04em; }
.stat-block .desc { font-size: 0.75rem; color: #555; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.06em; }

/* Callout */
.callout {
  background: #05080f;
  border: 1px solid #1e3a5f;
  border-left: 3px solid #3b82f6;
  border-radius: 6px;
  padding: 12px 16px;
  font-size: 0.85rem;
  color: #93c5fd;
  font-family: 'JetBrains Mono', monospace;
  line-height: 1.6;
}

/* Timeline */
.timeline-item {
  display: flex; gap: 16px; align-items: flex-start; margin-bottom: 16px;
}
.timeline-dot {
  width: 32px; height: 32px; min-width: 32px;
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-size: 0.75rem; font-weight: 700; font-family: 'JetBrains Mono', monospace;
}
.timeline-content h4 { margin: 0 0 4px; font-size: 0.875rem; font-weight: 600; color: #ededed; }
.timeline-content p  { margin: 0; font-size: 0.78rem; color: #666; line-height: 1.5; }

/* Transition arrow */
.arrow { color: #333; font-size: 1.1rem; margin: 0 8px; }

/* Hierarchy row */
.hier-row {
  display: flex; align-items: center; gap: 12px; padding: 10px 14px;
  border-radius: 6px; margin-bottom: 8px;
}

/* Appendix */
.qa-question { font-size: 0.95rem; font-weight: 600; color: #ffffff; margin-bottom: 8px; }
.qa-answer   { font-size: 0.835rem; color: #888; line-height: 1.7; }
</style>

---
layout: cover
---

# State-Space Compiler

<p style="color:#555; font-size:0.85rem; margin-top:8px; font-family:'JetBrains Mono',monospace">
Lab 2 &nbsp;·&nbsp; Formal Languages &amp; Finite Automata &nbsp;·&nbsp; Variant 13
</p>

<div style="margin-top:48px; display:flex; gap:12px; flex-wrap:wrap">
  <span class="label label-blue">NDFA → DFA</span>
  <span class="label label-green">Powerset Construction</span>
  <span class="label label-amber">Chomsky Linter</span>
  <span class="label label-gray">O(n) Inference</span>
</div>

<div style="position:absolute; bottom:32px; right:40px; text-align:right">
  <p style="font-size:0.72rem; color:#333; font-family:'JetBrains Mono',monospace; line-height:2">
    src/ndfa.py &nbsp;·&nbsp; src/powerset.py &nbsp;·&nbsp; src/grammar.py
  </p>
</div>

---

## The Problem

<div style="margin-top:24px; display:grid; grid-template-columns:1fr 1fr; gap:32px; align-items:start">

<div>

**An NDFA holds a fundamental contradiction.**

<div style="margin-top:20px">
<div class="callout">
δ(q₁, a) = { q₁, q₂ }
<br><br>
One input &rarr; two possible next states.<br>
The machine is in superposition.
</div>
</div>

<v-click>
<div style="margin-top:20px; font-size:0.85rem; color:#888; line-height:1.8">
You cannot deploy this. You cannot run this in O(n).<br>
You need to <strong style="color:#ededed">collapse</strong> the uncertainty.
</div>
</v-click>

</div>

<div>
<v-click>

**Variant 13 — the input data:**

<div style="margin-top:12px; background:#0d0d0d; border:1px solid #1f1f1f; border-radius:8px; padding:20px">
<table style="width:100%; font-family:'JetBrains Mono',monospace; font-size:0.78rem; border-collapse:collapse">
  <thead>
    <tr style="color:#444; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.06em">
      <th style="text-align:left; padding:4px 8px; border-bottom:1px solid #1f1f1f">δ</th>
      <th style="padding:4px 12px; border-bottom:1px solid #1f1f1f">a</th>
      <th style="padding:4px 12px; border-bottom:1px solid #1f1f1f">b</th>
    </tr>
  </thead>
  <tbody style="color:#ccc">
    <tr><td style="padding:4px 8px; color:#3b82f6; border-bottom:1px solid #141414">→ q₀</td><td style="padding:4px 12px; border-bottom:1px solid #141414">{q₀}</td><td style="padding:4px 12px; border-bottom:1px solid #141414">{q₁}</td></tr>
    <tr style="background:#1a0505"><td style="padding:4px 8px; color:#f87171; border-bottom:1px solid #141414">q₁</td><td style="padding:4px 12px; border-bottom:1px solid #141414"><strong style="color:#fca5a5">{q₁, q₂}</strong></td><td style="padding:4px 12px; border-bottom:1px solid #141414">{q₃}</td></tr>
    <tr><td style="padding:4px 8px; border-bottom:1px solid #141414">q₂</td><td style="padding:4px 12px; border-bottom:1px solid #141414">{q₁, q₂}</td><td style="padding:4px 12px; border-bottom:1px solid #141414">{q₃}</td></tr>
    <tr><td style="padding:4px 8px; color:#86efac">q₃ ✓</td><td style="padding:4px 12px">—</td><td style="padding:4px 12px">—</td></tr>
  </tbody>
</table>
</div>

<div style="margin-top:10px; font-size:0.72rem; color:#555; font-family:'JetBrains Mono',monospace">
Conflict detected: q₁ on 'a' → {q₁, q₂}
</div>

</v-click>
</div>

</div>

---

## Architecture

<p style="color:#555; font-size:0.82rem; margin-top:2px">Four independent modules. Each has a single responsibility.</p>

<div style="display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-top:28px">

<v-click>
<div class="module-card">
  <div style="margin-bottom:10px"><span class="label label-gray">01</span></div>
  <h3>JSON Router</h3>
  <p>Parses the automaton definition from <code>config/variant_N.json</code> into a typed 5-tuple (Q, Σ, δ, q₀, F). Single source of truth for all 32 variants.</p>
</div>
</v-click>

<v-click>
<div class="module-card">
  <div style="margin-bottom:10px"><span class="label label-amber">02</span></div>
  <h3>NDFA Diagnostic Engine</h3>
  <p><code>src/ndfa.py</code> — Scans the transition matrix. Flags any (state, symbol) pair that maps to a set of cardinality > 1. Outputs conflict coordinates.</p>
</div>
</v-click>

<v-click>
<div class="module-card">
  <div style="margin-bottom:10px"><span class="label label-blue">03</span></div>
  <h3>Powerset Compiler</h3>
  <p><code>src/powerset.py</code> — BFS over macro-states. Converts the N-dimensional superposition space into a flat, deterministic DFA. Worst case O(2ⁿ), practice O(n).</p>
</div>
</v-click>

<v-click>
<div class="module-card">
  <div style="margin-bottom:10px"><span class="label label-green">04</span></div>
  <h3>Chomsky Linter + Reverse Engineer</h3>
  <p><code>src/grammar.py</code> — Algebraically classifies grammar type (0–3). <code>DFA.to_grammar()</code> extracts formal production rules from the compiled automaton.</p>
</div>
</v-click>

</div>

---

## Mental Model — The Chomsky Hierarchy

<p style="color:#555; font-size:0.82rem; margin-top:2px">Why grammar classification matters before we touch the automaton.</p>

<div style="margin-top:24px; display:grid; grid-template-columns:1fr 1fr; gap:32px">

<div>

<div class="hier-row" style="background:#160c0a; border:1px solid #431407">
  <span class="label label-amber" style="min-width:60px; text-align:center">Type 0</span>
  <div><strong style="font-size:0.85rem">Unrestricted</strong><br><span style="font-size:0.75rem; color:#666">Turing-complete. No constraints.</span></div>
</div>
<div class="hier-row" style="background:#111; border:1px solid #1f1f1f; margin-left:16px">
  <span class="label label-gray" style="min-width:60px; text-align:center">Type 1</span>
  <div><strong style="font-size:0.85rem">Context-Sensitive</strong><br><span style="font-size:0.75rem; color:#666">|LHS| ≤ |RHS| always.</span></div>
</div>
<div class="hier-row" style="background:#111; border:1px solid #1f1f1f; margin-left:32px">
  <span class="label label-gray" style="min-width:60px; text-align:center">Type 2</span>
  <div><strong style="font-size:0.85rem">Context-Free</strong><br><span style="font-size:0.75rem; color:#666">LHS is a single non-terminal.</span></div>
</div>
<div class="hier-row" style="background:#052e16; border:1px solid #16a34a; margin-left:48px">
  <span class="label label-green" style="min-width:60px; text-align:center">Type 3</span>
  <div><strong style="font-size:0.85rem; color:#86efac">Regular — our target</strong><br><span style="font-size:0.75rem; color:#666">A → aB  or  A → a  only.</span></div>
</div>

</div>

<div>
<v-click>

**Our linter doesn't guess.** It algebraically verifies:

<div style="margin-top:16px; font-size:0.82rem; color:#888; line-height:2">

<div style="display:flex; align-items:center; gap:8px; margin-bottom:8px">
  <span class="label label-green">✓</span>
  <span>Every LHS is a <em>single</em> non-terminal</span>
</div>
<div style="display:flex; align-items:center; gap:8px; margin-bottom:8px">
  <span class="label label-green">✓</span>
  <span>Every RHS is <code>terminal</code> or <code>terminal NonTerminal</code></span>
</div>
<div style="display:flex; align-items:center; gap:8px; margin-bottom:8px">
  <span class="label label-green">✓</span>
  <span>Right-linear — non-terminal always at tail</span>
</div>

</div>

<div class="callout" style="margin-top:20px">
Variant 13 verdict: <strong>Type 3 — Regular Grammar</strong><br>
Provably equivalent to a finite automaton.
</div>

</v-click>
</div>

</div>

---

## Mental Model — NDFA Uncertainty

<p style="color:#555; font-size:0.82rem">Non-determinism as parallel computation branches.</p>

<div style="margin-top:24px; display:grid; grid-template-columns:3fr 2fr; gap:32px">

<div>

<div style="font-size:0.82rem; color:#888; line-height:1.9; margin-bottom:20px">
When the NDFA reads <code>a</code> at state q₁, it doesn't choose — it <strong style="color:#ededed">splits</strong> into both branches simultaneously. This is the non-deterministic moment.
</div>

<div style="display:flex; flex-direction:column; gap:8px">

<div style="display:flex; align-items:center; gap:0">
  <div style="background:#1a1a1a; border:1px solid #2a2a2a; border-radius:50%; width:36px; height:36px; display:flex; align-items:center; justify-content:center; font-family:'JetBrains Mono',monospace; font-size:0.75rem; color:#3b82f6">q₁</div>
  <div style="flex:1; height:1px; background:linear-gradient(90deg,#3b82f6,transparent)"></div>
  <div style="background:#1a1a1a; border:1px solid #2a2a2a; padding:4px 12px; border-radius:4px; font-family:'JetBrains Mono',monospace; font-size:0.72rem; color:#555">read 'a'</div>
  <div style="flex:1; height:1px; background:transparent"></div>
</div>

<div style="display:flex; gap:32px; padding-left:36px; margin-top:4px">
  <div style="display:flex; flex-direction:column; align-items:center; gap:4px">
    <div style="width:1px; height:20px; background:#dc2626"></div>
    <div style="background:#450a0a; border:1px solid #dc2626; border-radius:50%; width:36px; height:36px; display:flex; align-items:center; justify-content:center; font-family:'JetBrains Mono',monospace; font-size:0.75rem; color:#fca5a5">q₁</div>
    <span style="font-size:0.7rem; color:#555; font-family:'JetBrains Mono',monospace">Branch A</span>
  </div>
  <div style="display:flex; flex-direction:column; align-items:center; gap:4px">
    <div style="width:1px; height:20px; background:#dc2626"></div>
    <div style="background:#450a0a; border:1px solid #dc2626; border-radius:50%; width:36px; height:36px; display:flex; align-items:center; justify-content:center; font-family:'JetBrains Mono',monospace; font-size:0.75rem; color:#fca5a5">q₂</div>
    <span style="font-size:0.7rem; color:#555; font-family:'JetBrains Mono',monospace">Branch B</span>
  </div>
</div>

</div>

<v-click>
<div class="callout" style="margin-top:20px">
In simulation this requires exponential backtracking.<br>
In a real engine deployment — <strong>not viable</strong>.
</div>
</v-click>

</div>

<div>
<v-click>

**Why this is a compiler problem:**

<div style="margin-top:16px; font-size:0.82rem; color:#888; line-height:2">

A Python regex engine can't branch — it runs on actual hardware with a single instruction pointer.

Every production NDFA must be **compiled** to a DFA before deployment.

</div>

<div style="margin-top:16px; background:#0d0d0d; border:1px solid #1f1f1f; border-radius:6px; padding:14px">
  <div style="font-size:0.72rem; color:#555; font-family:'JetBrains Mono',monospace; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:8px">Complexity</div>
  <div style="display:flex; justify-content:space-between; font-family:'JetBrains Mono',monospace; font-size:0.82rem">
    <span style="color:#f87171">NDFA simulation</span>
    <span style="color:#f87171">O(2ⁿ)</span>
  </div>
  <div style="display:flex; justify-content:space-between; font-family:'JetBrains Mono',monospace; font-size:0.82rem; margin-top:4px">
    <span style="color:#86efac">DFA execution</span>
    <span style="color:#86efac">O(n)</span>
  </div>
</div>

</v-click>
</div>

</div>

---
layout: two-cols
---

## Snippet 1 — Uncertainty Detector

<p style="color:#555; font-size:0.8rem">src/ndfa.py · lines 62–73</p>

<div style="margin-top:20px; font-size:0.8rem; color:#888; line-height:1.8">
<strong style="color:#ededed">What to say:</strong>
<br><br>
"This is my Uncertainty Detector. It scans the transition matrix. If a single state-input tuple maps to a set with cardinality greater than one, it flags the system as non-deterministic."
</div>

<div style="margin-top:24px">
<div class="callout">
Key insight: the data structure itself encodes the problem.<br>
<code>δ: (state, symbol) → frozenset[str]</code><br><br>
A DFA is just the degenerate case where <code>|frozenset| ≤ 1</code>.
</div>
</div>

::right::

<div style="padding-left:24px; margin-top:44px">

```python {all|4|7-10|all}
# src/ndfa.py

def is_deterministic(self) -> bool:
    """True iff every (state, symbol) → |targets| ≤ 1."""
    return all(
        len(targets) <= 1
        for targets in self.transitions.values()
    )

def non_deterministic_sources(self):
    """All (state, symbol) pairs that cause non-determinism."""
    return [
        (state, sym)
        for (state, sym), targets
            in self.transitions.items()
        if len(targets) > 1     # ← the critical condition
    ]
```

<div style="margin-top:16px; font-size:0.75rem; color:#555; font-family:'JetBrains Mono',monospace; line-height:1.8">
Variant 13 output:<br>
<span style="color:#fca5a5">non_deterministic_sources() → [('q1','a'), ('q2','a')]</span>
</div>

</div>

---
layout: two-cols
---

## Mental Model — Powerset Construction

<p style="color:#555; font-size:0.8rem">The core insight behind Snippet 2</p>

<div style="margin-top:20px">

<div style="font-size:0.82rem; color:#888; line-height:1.9">
Treat <strong style="color:#ededed">combinations of NDFA states</strong> as single new nodes.
</div>

<div style="margin-top:20px; display:flex; flex-direction:column; gap:10px">

<div class="hier-row" style="background:#03173a; border:1px solid #2563eb">
  <span class="label label-blue" style="min-width:80px; text-align:center">{q₀}</span>
  <span style="font-size:0.78rem; color:#888">Start — same as NDFA start</span>
</div>

<div class="hier-row" style="background:#111; border:1px solid #1f1f1f">
  <span class="label label-gray" style="min-width:80px; text-align:center">{q₁}</span>
  <span style="font-size:0.78rem; color:#888">After first 'b'</span>
</div>

<div class="hier-row" style="background:#1a0a0a; border:1px solid #dc2626">
  <span class="label label-red" style="min-width:80px; text-align:center">{q₁,q₂}</span>
  <span style="font-size:0.78rem; color:#888"><strong style="color:#fca5a5">New macro-state</strong> — the union of q₁ and q₂</span>
</div>

<div class="hier-row" style="background:#052e16; border:1px solid #16a34a">
  <span class="label label-green" style="min-width:80px; text-align:center">{q₃} ✓</span>
  <span style="font-size:0.78rem; color:#888">Accepting — inherited from q₃ ∈ F</span>
</div>

<div class="hier-row" style="background:#111; border:1px solid #333">
  <span class="label label-gray" style="min-width:80px; text-align:center">∅</span>
  <span style="font-size:0.78rem; color:#888">Dead/trap state — mathematical completeness</span>
</div>

</div>

</div>

::right::

<div style="padding-left:24px; margin-top:44px">

<div style="font-size:0.8rem; color:#888; line-height:2; margin-bottom:16px">
<strong style="color:#ededed">Result:</strong> 4 NDFA states → 5 DFA macro-states.
Worst case was 2⁴ = 16.
BFS pruned 11 unreachable states.
</div>

<div style="background:#0d0d0d; border:1px solid #1f1f1f; border-radius:8px; padding:16px">
<table style="width:100%; font-family:'JetBrains Mono',monospace; font-size:0.72rem; border-collapse:collapse">
  <thead>
    <tr style="color:#444; text-transform:uppercase; letter-spacing:0.05em">
      <th style="text-align:left; padding:4px 6px; border-bottom:1px solid #1f1f1f">Macro-state</th>
      <th style="padding:4px 8px; border-bottom:1px solid #1f1f1f">a</th>
      <th style="padding:4px 8px; border-bottom:1px solid #1f1f1f">b</th>
      <th style="padding:4px 6px; border-bottom:1px solid #1f1f1f">Accept</th>
    </tr>
  </thead>
  <tbody style="color:#ccc">
    <tr><td style="padding:4px 6px; color:#3b82f6; border-bottom:1px solid #141414">{q₀}</td><td style="padding:4px 8px; border-bottom:1px solid #141414">{q₀}</td><td style="padding:4px 8px; border-bottom:1px solid #141414">{q₁}</td><td style="padding:4px 6px; border-bottom:1px solid #141414"></td></tr>
    <tr><td style="padding:4px 6px; border-bottom:1px solid #141414">{q₁}</td><td style="padding:4px 8px; border-bottom:1px solid #141414; color:#fca5a5">{q₁,q₂}</td><td style="padding:4px 8px; border-bottom:1px solid #141414">{q₃}</td><td style="padding:4px 6px; border-bottom:1px solid #141414"></td></tr>
    <tr style="background:#1a0a0a"><td style="padding:4px 6px; border-bottom:1px solid #141414; color:#fca5a5">{q₁,q₂}</td><td style="padding:4px 8px; border-bottom:1px solid #141414; color:#fca5a5">{q₁,q₂}</td><td style="padding:4px 8px; border-bottom:1px solid #141414">{q₃}</td><td style="padding:4px 6px; border-bottom:1px solid #141414"></td></tr>
    <tr style="background:#052e16"><td style="padding:4px 6px; color:#86efac; border-bottom:1px solid #141414">{q₃}</td><td style="padding:4px 8px; border-bottom:1px solid #141414">∅</td><td style="padding:4px 8px; border-bottom:1px solid #141414">∅</td><td style="padding:4px 6px; border-bottom:1px solid #141414; color:#86efac">yes</td></tr>
    <tr><td style="padding:4px 6px; color:#555">∅</td><td style="padding:4px 8px; color:#555">∅</td><td style="padding:4px 8px; color:#555">∅</td><td style="padding:4px 6px"></td></tr>
  </tbody>
</table>
</div>

</div>

---
layout: two-cols
---

## Snippet 2 — Macro-State Generator

<p style="color:#555; font-size:0.8rem">src/powerset.py · powerset_construction()</p>

<div style="margin-top:20px; font-size:0.8rem; color:#888; line-height:1.8">
<strong style="color:#ededed">What to say:</strong>
<br><br>
"This is the Subset Construction algorithm. A queue-based BFS — it dynamically discovers new macro-states by calculating the union of all reachable NDFA targets. It runs until the state-space stabilizes."
</div>

<div style="margin-top:16px">
<div class="callout">
The <code>visited</code> dict is both the memo-table and the state registry. <code>queue</code> drives the BFS. The algorithm terminates because 2ⁿ is finite.
</div>
</div>

::right::

<div style="padding-left:24px; margin-top:44px">

```python {all|5-7|9-11|13-18|20-21|all}
# src/powerset.py

def powerset_construction(ndfa, include_dead=True):
    start_macro = frozenset({ndfa.start})
    visited = {start_macro: label(start_macro)}
    queue   = deque([start_macro])   # BFS driver

    while queue:                     # stabilize
        macro = queue.popleft()

        for sym in ndfa.alphabet:
            # Union of all δ(qᵢ, sym) for qᵢ ∈ macro
            nxt = frozenset(
                t
                for qi in macro
                for t in ndfa.delta(qi, sym)
            )                        # ← the macro-state kernel

            if nxt not in visited:   # new state discovered
                visited[nxt] = label(nxt)
                queue.append(nxt)    # explore it next
```

</div>

---
layout: two-cols
---

## Snippet 3 — Reverse Engineer

<p style="color:#555; font-size:0.8rem">src/powerset.py · DFA.to_grammar()</p>

<div style="margin-top:20px; font-size:0.8rem; color:#888; line-height:1.8">
<strong style="color:#ededed">What to say:</strong>
<br><br>
"Once the optimized DFA is generated, this module mathematically reads the topology back out as a formal grammar — completing the compile-and-verify lifecycle."
</div>

<div style="margin-top:16px">
<div class="callout">
Every DFA edge <code>(qᵢ, c) → qⱼ</code> maps to:<br>
&nbsp;&nbsp;qᵢ → c qⱼ &nbsp;(continuation)<br>
&nbsp;&nbsp;qᵢ → c &nbsp;&nbsp;&nbsp;(if qⱼ ∈ F, termination)
</div>
</div>

::right::

<div style="padding-left:24px; margin-top:44px">

```python {all|5-7|8-9|10|all}
# src/powerset.py  ·  DFA.to_grammar()

def to_grammar(self):
    productions = []
    for (qi, c), qj in self.transitions.items():
        if qj == self.DEAD_LABEL:
            continue               # dead edges produce nothing
        if qj in self.accepting:
            productions.append((qi, c))          # qᵢ → c
        productions.append((qi, f"{c} {qj}"))    # qᵢ → c qⱼ

    for state in self.accepting:
        productions.append((state, ""))           # qⱼ → ε

    return _dedup(productions)
```

<div style="margin-top:16px; font-size:0.75rem; color:#555; font-family:'JetBrains Mono',monospace; line-height:1.8">
Sample output — Variant 13 DFA grammar:<br>
<span style="color:#a3e635">
{q₀} → b {q₁}<br>
{q₁} → a {q₁,q₂} | b {q₃}<br>
{q₃} → ε
</span>
</div>

</div>

---

## The Numbers — Variant 13

<p style="color:#555; font-size:0.82rem">What the pipeline produces. These are the facts to quote.</p>

<div style="display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-top:28px">

<div class="stat-block">
  <div class="num" style="color:#f87171">4</div>
  <div class="desc">NDFA states</div>
</div>

<div class="stat-block">
  <div class="num" style="color:#3b82f6">5</div>
  <div class="desc">DFA macro-states</div>
</div>

<div class="stat-block">
  <div class="num" style="color:#86efac">11</div>
  <div class="desc">states pruned<br><span style="font-size:0.65rem">(of 2⁴ = 16 worst-case)</span></div>
</div>

<div class="stat-block">
  <div class="num" style="color:#a3e635">O(n)</div>
  <div class="desc">DFA inference<br><span style="font-size:0.65rem">vs O(2ⁿ) NDFA sim</span></div>
</div>

</div>

<div style="display:grid; grid-template-columns:1fr 1fr; gap:24px; margin-top:24px">

<div>
<div style="font-size:0.72rem; color:#555; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:10px">Language accepted by Variant 13</div>
<div class="callout" style="font-size:0.9rem">
L(M) = a<sup>*</sup> b a<sup>*</sup> b a<sup>*</sup>
<div style="margin-top:8px; font-size:0.75rem; color:#666">
"Any number of a's, then a b, then any number of a's, then b and a's"<br>
Exactly 2 b's — second b drives into the accepting state {q₃}.
</div>
</div>
</div>

<div>
<v-click>
<div style="font-size:0.72rem; color:#555; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:10px">Test cases</div>
<div style="background:#0d0d0d; border:1px solid #1f1f1f; border-radius:6px; padding:16px">
<table style="width:100%; font-family:'JetBrains Mono',monospace; font-size:0.78rem; border-collapse:collapse">
  <thead><tr style="color:#444; font-size:0.7rem"><th style="text-align:left; padding:3px 6px; border-bottom:1px solid #1f1f1f">String</th><th style="padding:3px 6px; border-bottom:1px solid #1f1f1f">Result</th><th style="padding:3px 6px; border-bottom:1px solid #1f1f1f">Final state</th></tr></thead>
  <tbody>
    <tr><td style="padding:3px 6px; border-bottom:1px solid #111">ab</td><td style="padding:3px 6px; color:#86efac; border-bottom:1px solid #111">accept</td><td style="padding:3px 6px; color:#555; border-bottom:1px solid #111">{q₃}</td></tr>
    <tr><td style="padding:3px 6px; border-bottom:1px solid #111">bab</td><td style="padding:3px 6px; color:#86efac; border-bottom:1px solid #111">accept</td><td style="padding:3px 6px; color:#555; border-bottom:1px solid #111">{q₃}</td></tr>
    <tr><td style="padding:3px 6px; border-bottom:1px solid #111">abab</td><td style="padding:3px 6px; color:#86efac; border-bottom:1px solid #111">accept</td><td style="padding:3px 6px; color:#555; border-bottom:1px solid #111">{q₃}</td></tr>
    <tr><td style="padding:3px 6px; border-bottom:1px solid #111">aba</td><td style="padding:3px 6px; color:#f87171; border-bottom:1px solid #111">reject</td><td style="padding:3px 6px; color:#555; border-bottom:1px solid #111">∅</td></tr>
    <tr><td style="padding:3px 6px">bbb</td><td style="padding:3px 6px; color:#f87171">reject</td><td style="padding:3px 6px; color:#555">∅</td></tr>
  </tbody>
</table>
</div>
</v-click>
</div>

</div>

---

## Q&A — Dead State ∅

<p style="color:#555; font-size:0.82rem">If asked: "What is the dead state for?"</p>

<div style="margin-top:24px">

<div class="qa-question">"What is the Dead State (∅) for?"</div>

<div class="qa-answer">
In an NDFA, if there is no transition defined, the branch simply dies — the machine makes no move.
<br><br>
But a DFA must be <strong style="color:#ededed">mathematically complete</strong>. By the formal definition, every state must have exactly one transition for every symbol in Σ. If there is no valid move, we need somewhere to go.
<br><br>
The Dead State ∅ is a <strong style="color:#ededed">trap/sink state</strong>. Once entered, all transitions loop back into it. It allows undefined inputs to be handled without breaking determinism.
<br><br>
It is the difference between a <em>partial</em> transition function (NDFA) and a <em>total</em> transition function (DFA).
</div>

</div>

::right::

<div style="padding-left:24px; margin-top:44px">

```
State  Symbol  Next
─────────────────────
{q₃}    a      ∅      ← no valid move
{q₃}    b      ∅      ← no valid move
∅       a      ∅      ← trap: stays here
∅       b      ∅      ← trap: stays here
```

<div style="margin-top:20px" class="callout">
Without ∅, the DFA table has holes.<br>
With ∅, the transition function δ: Q × Σ → Q<br>
is defined for <strong>every</strong> element of Q × Σ.<br><br>
Total function → formal correctness.
</div>

</div>

---
layout: two-cols
---

## Q&A — Real-World Use

<p style="color:#555; font-size:0.82rem">If asked: "Why is powerset construction useful in practice?"</p>

<div style="margin-top:24px">

<div class="qa-question">"Why does this matter outside academia?"</div>

<div class="qa-answer">
It is precisely how <strong style="color:#ededed">regular expression engines compile</strong> under the hood.
<br><br>
When you write <code style="color:#a3e635">/a*b/</code>, you are writing in NFA notation — it is concise and human-readable because it describes the pattern non-deterministically.
<br><br>
The regex engine (<code style="color:#a3e635">re</code>, PCRE, V8) then <strong style="color:#ededed">automatically applies powerset construction</strong> to compile that NFA into a DFA so the actual string scan runs in O(n) time without backtracking.
<br><br>
Without this compilation step, searching a 1 GB log file with a regex would require exponential backtracking at every character — it would never finish.
</div>

</div>

::right::

<div style="padding-left:24px; margin-top:44px">

<div style="font-size:0.72rem; color:#555; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:12px">The compile pipeline (regex engine)</div>

<div style="display:flex; flex-direction:column; gap:10px">

<div style="background:#111; border:1px solid #1f1f1f; border-radius:6px; padding:10px 14px; font-family:'JetBrains Mono',monospace; font-size:0.78rem">
  <span style="color:#555">human writes</span><br>
  <span style="color:#a3e635">re.compile(r"/a*bab/")</span>
</div>

<div style="text-align:center; color:#333; font-size:0.8rem">↓ parse → NFA</div>

<div style="background:#1a0505; border:1px solid #3b0f0f; border-radius:6px; padding:10px 14px; font-family:'JetBrains Mono',monospace; font-size:0.78rem; color:#fca5a5">
  Non-deterministic NFA<br>
  <span style="color:#555">O(2ⁿ) to simulate</span>
</div>

<div style="text-align:center; color:#3b82f6; font-size:0.8rem">↓ powerset construction</div>

<div style="background:#052e16; border:1px solid #16a34a; border-radius:6px; padding:10px 14px; font-family:'JetBrains Mono',monospace; font-size:0.78rem; color:#86efac">
  Deterministic DFA<br>
  <span style="color:#555">O(n) to execute</span>
</div>

</div>

</div>

---
layout: center
---

<div style="text-align:center">

<div style="font-size:0.72rem; color:#555; font-family:'JetBrains Mono',monospace; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:20px">
Lab 2 · Variant 13
</div>

<h1 style="font-size:2.2rem; letter-spacing:-0.04em; color:#ffffff; margin-bottom:8px">
State-Space Compiler
</h1>

<p style="color:#555; font-size:0.85rem; font-family:'JetBrains Mono',monospace">
src/ndfa.py &nbsp;&middot;&nbsp; src/powerset.py &nbsp;&middot;&nbsp; src/grammar.py
</p>

<div style="display:flex; gap:10px; justify-content:center; margin-top:32px; flex-wrap:wrap">
  <span class="label label-blue">48 tests passing</span>
  <span class="label label-green">O(n) inference</span>
  <span class="label label-amber">Chomsky Type 3</span>
  <span class="label label-gray">Interactive dashboard</span>
</div>

<div style="margin-top:48px; font-size:0.8rem; color:#333; font-family:'JetBrains Mono',monospace">
streamlit run app.py
</div>

</div>
