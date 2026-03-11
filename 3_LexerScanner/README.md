# TensorScript Lexer

## Course: Formal Languages & Finite Automata
## Author: Lucian Adrian

----

## Theory

Lexical analysis is the compiler stage that transforms raw source text into a stream of typed tokens. In practical machine learning terms, it behaves like a preprocessing pipeline: unstructured characters are normalized, classified, and annotated with metadata before any higher-level interpretation happens.

For this laboratory work I avoided the usual calculator example and designed a lexer for TensorScript, a small domain-specific language for tensor literals, activation functions, and matrix-oriented expressions. This still satisfies the laboratory requirements for floating-point numbers and trigonometric functions, but reframes them in a data-science setting that is closer to the systems I want to build.

The implementation uses immutable, strongly typed tokens and a lazy generator-based scanning pipeline. Because tokens are yielded one-by-one, the lexer can stream source code with constant auxiliary memory, $O(1)$, aside from the current token being built.

## Objectives

* Understand how lexical analysis works in a compiler frontend.
* Build a tokenizer that supports floats, integers, identifiers, keywords, comments, and mathematical functions.
* Track exact source coordinates for each token to support professional diagnostics.
* Present the token stream as structured data using a polished terminal interface.
* Demonstrate clean architecture, tests, and extensibility beyond the minimum lab requirements.

## TensorScript Language Slice

The lexer recognizes a compact ML-oriented syntax such as:

```tensorscript
// Define a neural network layer
let weights = [[0.5, -0.1], [sin(0.2), relu(0.9)]];
let bias = [1.0, 0.0];
let output = softmax([1, 2, 3]);
```

Supported lexical categories include:

* Keywords: `let`, `def`, `return`
* Identifiers: `weights`, `bias`, `hidden_layer`
* Math functions: `sin`, `cos`, `tan`, `relu`, `softmax`, `exp`, `log`
* Numeric literals: integers and floats
* Matrix punctuation: `[ ]`, `( )`, `,`, `;`, `=`
* Operators: `+`, `-`, `*`, `/`
* Line comments: `// ...`

## Implementation Description

### Architecture

The solution is split into small modules with single responsibilities.

* `src/tokens.py` defines immutable token objects, token kinds, token families, and source span metadata.
* `src/lexer.py` contains the lazy TensorScript scanner and the structured lexical diagnostic engine.
* `src/highlighter.py` reconstructs the original source code with ANSI coloring based on token families.
* `main.py` is the CLI entry point that renders a Rich token table, summary dashboard, JSON export, and highlighted source.
* `app.py` is the Streamlit Observatory dashboard with interactive token analytics, syntax highlighting, diagnostics, and architecture panels. It features an ACE-powered live code editor and a JSON download button for tokens.
* `tests/test_lexer.py` validates correctness, token positions, diagnostics, highlighting, and language coverage.

### Strong Typing and Memory Efficiency

Tokens are implemented as frozen dataclasses with `slots=True`. This gives a clean immutable model, better memory discipline, and explicit type annotations. Each token stores its exact line, column, byte offset range, lexeme, semantic value, and memory address for display.

### Lazy Scanning

The lexer exposes a generator via `tokenize()`. This means the consumer may iterate token-by-token without forcing the entire source file to be eagerly materialized as a token list. For CLI rendering and tests I also provide `collect()`, but the core engine remains streaming.

### Diagnostic Engine

When invalid source is encountered, the lexer raises a custom `LexicalError` that formats a compiler-style message with line, column, source excerpt, caret pointer, and offending lexeme. Example:

```text
Lexical Error at Line 1, Column 15 in <memory>:
let weights = @[0.5];
              ^
Unrecognized token. Offending lexeme: '@'.
```

### Visualization Layer

The CLI prints a rich table with:

* Line
* Column
* Token Type
* Lexeme
* Memory Address

It also prints a syntax-highlighted reconstruction of the original TensorScript program, turning the lexer into a presentable demo rather than a raw debug dump.

### Streamlit Observatory

To push the lab beyond a terminal-only demo, the project now includes a Streamlit dashboard called TensorScript Observatory. It provides:

* an input studio for sample sources and uploaded files
* KPI cards with token density sparklines
* an interactive token matrix
* a syntax-colored source lens
* a diagnostic showcase for invalid code
* an architecture tab that exposes the typed token model and generator core
* export tokens as JSON for offline analysis

## Project Structure

```text
3_LexerScanner/
|-- examples/
|   |-- batch_norm_demo.tscript
|   |-- tensorscript_demo.tscript
|   |-- transformer_block.tscript
|   `-- tensorscript_invalid.tscript
|-- presentation/
|   |-- MENTAL_MODEL.md
|   |-- PRESENTATION_SCRIPT.md
|   `-- slides.md
|-- reports/
|   `-- REPORT.md
|-- src/
|   |-- __init__.py
|   |-- highlighter.py
|   |-- lexer.py
|   `-- tokens.py
|-- tests/
|   `-- test_lexer.py
|-- main.py
|-- requirements.txt
|-- README.md
`-- task.md
```

## Usage

### Installation

```powershell
cd 3_LexerScanner
pip install -r requirements.txt
```

### Run the Demo

```powershell
python main.py --demo --stats
```

### Launch the Dashboard

```powershell
streamlit run app.py
```

### Analyze a File

```powershell
python main.py --file examples/tensorscript_demo.tscript --json --stats
```

### Analyze Inline Code

```powershell
python main.py --code "let weights = [[0.5, -0.1], [sin(0.2), relu(0.9)]];"
```

### Run the Tests

```powershell
pytest tests -v
```

## Results

The final product is intentionally over-scoped compared to the minimum requirement:

* A non-trivial DSL instead of a calculator.
* Lazy token streaming with typed immutable objects.
* Exact source-span tracking for every lexeme.
* Compiler-style diagnostics.
* Rich terminal dashboards and syntax highlighting.
* A full Streamlit observatory for interactive analysis.
* A presentation deck and speaker script for formal demonstration.
* A focused but serious automated test suite.

This makes the laboratory work look closer to a real compiler frontend than a classroom script.

## References

* LLVM Tutorial: https://llvm.org/docs/tutorial/MyFirstLanguageFrontend/LangImpl01.html
* Python Dataclasses Documentation: https://docs.python.org/3/library/dataclasses.html
* Python Enum Documentation: https://docs.python.org/3/library/enum.html
* Rich Table Documentation: https://rich.readthedocs.io/en/stable/tables.html
* Streamlit Documentation: https://docs.streamlit.io/
