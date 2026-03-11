---
theme: seriph
background: https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=2564&auto=format&fit=crop
class: text-center
highlighter: shiki
lineNumbers: false
info: |
  ## TensorScript Lexer
  A sophisticated, SOLID Lexer implemented in Python for standard DSL building.
drawings:
  persist: false
transition: slide-up
title: TensorScript Lexer Deep-Dive
mdc: true
---

# TensorScript Lexical Analysis
## The Foundation of a Modern DSL 🚀

A comprehensive, $O(1)$ Memory stream architecture adhering to SOLID boundaries.

<div class="pt-12">
  <span @click="$slidev.nav.next" class="px-2 py-1 rounded cursor-pointer" hover="bg-white bg-opacity-10">
    Press Space to begin our Journey <carbon:arrow-right class="inline"/>
  </span>
</div>

---
transition: fade-out
---

# 🧠 The Mental Model
## From Chaos to Categorized Tokens

We begin with the simplest observation: a program is just a sequence of characters. The lexer collapses noise and surfaces structure.

Lexical analysis is about collapsing noise (spaces, comments) and recognizing signals (keywords, values).

<v-clicks>

- **Raw Source:** Endless streams of ASCII/Unicode chunks.
- **Filtering:** Removing whitespace and inline `//` comments safely.
- **Grouping:** Combining `[` `1` `.` `0` `]` into meaningful typed bundles.
- **Output:** Clean Token Iterators ready for the Syntactic Parser.

</v-clicks>

<br/>

<div v-click class="p-4 bg-gray-100 dark:bg-gray-800 rounded-lg shadow">
💡 <b>Meta-Thought:</b> A great Lexer is invisible. It handles memory lazily so large files don't crush the system.
</div>

---

# 🧩 What is a Token?

Before writing any code, the simplest question is: how do we turn characters into words? A human reader groups letters into words automatically; a lexer formalizes that process. Consider input:

```
let x = 42;
```

Type-by-type: `[let] [x] [=] [42] [;]` then categorize each piece as keyword/identifier/assign/integer/semicolon.

<v-clicks>

- characters → grouped lexemes
- lexemes → types
- types → tokens passed to parser

</v-clicks>

Teach the concept from first principles: start as though the audience has no prior knowledge.

---
layout: default
---

# 📐 The SOLID Architecture
## How We Engineered It Iteratively

*Architecture is geometry applied to software. We draw clean boundaries and then prove they hold under change.*

<div class="grid grid-cols-2 gap-4">
<div>

### S. O. L. I. D Breakdown

- <span v-mark.1><b>Single Responsibility:</b> `tokens.py` vs `lexer.py` vs `highlighter.py` - strictly separated.</span>
- <span v-mark.2><b>Open/Closed:</b> `LexerConfig` extends configurations without source changes.</span>
- <span v-mark.3><b>Liskov Substitution:</b> Custom `LexicalError` integrates gracefully with native implementations.</span>
- <span v-mark.4><b>Interface Segregation:</b> Relying heavily on iterables.</span>
- <span v-mark.5><b>Dependency Inversion:</b> Enum contracts over hardcoded strings.</span>

</div>

<div class="flex items-center justify-center">
  <img src="https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=2670&auto=format&fit=crop" class="rounded shadow-xl h-64 object-cover" />
</div>
</div>

---
layout: center
class: text-center
---

# ⚙️ Inside the $O(1)$ Generator
## Watch It Stream!

Here is the actual loop – simple yet powerful. We avoid buffering the entire file, yielding tokens as soon as they are recognized.

Instead of reading a whole file and maintaining a huge list:
```python {all|2|3-4|5-8|all}
def tokenize(self) -> Generator[Token, None, None]:
    while not self._is_at_end():
        current = self._peek()
        # WhiteSpace Skipped Lazily...
        if current.isalpha():
            yield self._scan_identifier_or_keyword()
        # ...
```
We actively `yield` exactly when needed!

---
layout: iframe-right
url: http://localhost:8501
---

# 🎛️ The Observatory
## The Streamlit Dashboard

The observatory makes the invisible visible.
Use the ACE editor to type code, see metrics update, browse token tables, and download JSON.  
All built on the exact same lexer we test and ship.

<v-clicks>

1. **Live Highlights**: Real-time syntax detection via the ACE editor.
2. **Metrics**: Token density, distribution, speed (μs).
3. **Graphviz Visualization**: Abstract syntax lifecycle paths.
4. **DataFrames**: Tabular exports mappings coordinates.
5. **Download**: Export tokens as JSON from the dashboard.

</v-clicks>

*(Requires `streamlit run app.py` on the left context.)*

---

# 🧠 Recap

We explained each concept from first principles:
- Characters → tokens → data model → interfaces
- Error messages mimic human language feedback
- Design choices guided by simplicity and clarity

---

# 🛠 Token Types & Data Model

Tokens are just Python dataclasses.  
Each one knows its type, lexeme, location, and value.

```python
@dataclass(frozen=True, slots=True)
class Token:
    token_type: TokenType
    lexeme: str
    span: SourceSpan
    value: Any = None
```

Solid typing lets us reason about them mathematically.

---

# 🔍 Diagnostics

Errors should point with a caret, show the snippet, and tell you what went wrong.
This is what real compilers do, and it is easy once tokens carry spans.

```text
Lexical Error at Line 1, Column 15 in file.tscript:
let weights = @[0.5];
              ^
Unrecognized token. Offending lexeme: '@'.
```

Each component (word, position, message) is derived from the token stream.

---

---
layout: cover
background: https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=2670&auto=format&fit=crop
---

# 📦 Real-World Use Cases

TensorScript could serve as:

- A configuration language for neural network layers.
- A preprocessing DSL in data pipelines.
- An embedded scripting language for hyperparameter sampling.

```tensorscript
// define layer weights
let w = [[0.1, 0.2],[0.3,0.4]];
let act = relu;
```

These examples make the language feel concrete and practical.

---

# 🏁 Conclusion & Future Polish

The Lexer is perfectly polished according to our checklist:
- We started from characters, built tokens, then built interfaces.
- We proved correctness with tests and diagnostics.
- We created tooling that explains itself.

Future work: parser, AST, codegen, integration with ML models, CI pipelines, open-source library.

*The best projects are those that teach someone else how to build them.*
