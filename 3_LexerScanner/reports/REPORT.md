# TensorScript Lexer Frontend

### Course: Formal Languages & Finite Automata
### Author: Lucian Adrian

----

## Theory

Lexical analysis segments source code into tokens that later compilation phases can reason about. In this laboratory work, the lexer is framed as a data preprocessing stage for compilers: raw text is mapped into a structured, typed stream with coordinate metadata and semantic labels.

## Objectives:

* Implement a sample lexer for a non-trivial language.
* Support floating-point literals and trigonometric functions.
* Provide exact token coordinates for diagnostics.
* Use clean architecture and strong typing.
* Demonstrate the lexer with polished terminal output.

## Implementation description

* The language is TensorScript, a small DSL for tensor literals and neural-network-style mathematical expressions.
* Tokens are represented with immutable dataclasses and enums, which gives a strongly typed and extensible model.
* The lexer scans source lazily with a generator, yielding tokens one-by-one.
* Errors are reported through a custom `LexicalError` that prints source line, column, caret, and message.
* A syntax highlighter rebuilds the original source code with ANSI colors.
* The CLI prints a token table, lexer summary, highlighted source, and optional JSON export.
* A Streamlit dashboard turns the lexer into an interactive observatory with metrics, token tables, diagnostics, and architecture explanations.

Example input:

```tensorscript
let weights = [[0.5, -0.1], [sin(0.2), relu(0.9)]];
let bias = [1.0, 0.0];
```

Example diagnostic:

```text
Lexical Error at Line 1, Column 15 in <memory>:
let weights = @[0.5];
              ^
Unrecognized token. Offending lexeme: '@'.
```

## Conclusions / Screenshots / Results

The project satisfies the lab requirements while going substantially beyond them. Instead of a calculator, it demonstrates lexical analysis in a machine-learning DSL context. The final product is modular, tested, memory-conscious, and polished enough for presentation.

## References

* https://llvm.org/docs/tutorial/MyFirstLanguageFrontend/LangImpl01.html
* https://docs.python.org/3/library/dataclasses.html
* https://docs.python.org/3/library/enum.html
* https://rich.readthedocs.io/en/stable/tables.html
