# TensorScript Observatory Presentation Script

## Slide 1 — Title

Today I am presenting Lab 3, but instead of building the standard calculator lexer, I designed the lexical frontend for TensorScript, a small domain-specific language for matrix operations and activation functions. The goal was not only to satisfy the formal requirements, but to present the lab like a real compiler subsystem.

## Slide 2 — Why TensorScript?

The usual calculator example is functionally correct, but academically predictable. TensorScript still includes floats and trigonometric functions, which were explicitly requested in the assignment, but places them in a machine-learning context. This makes the lexer feel relevant to data science and DSL engineering rather than to a toy arithmetic parser.

## Slide 3 — Language Design

Here I quickly describe the elementary tokens that make up TensorScript, starting from letters and digits as though the listener knows nothing. You do not assume prior knowledge; you build understanding from text.

The language slice includes declarations such as `let`, identifiers like `weights`, numeric literals, matrix punctuation, and mathematical functions including `sin`, `relu`, and `softmax`. That means the token stream is rich enough to demonstrate realistic lexical diversity while still remaining manageable for a laboratory project.

## Slide 4 — Architecture

Before architecture I added a new slide called “What is a Token?” — this is where I explain that tokens are just groups of characters, like words in a sentence. It helps ground the audience in first principles.

I split the implementation into focused modules. `tokens.py` defines the type system for tokens, `lexer.py` implements the lazy scanner and diagnostics, `highlighter.py` reconstructs colorized source, `main.py` handles the command-line interface, and `app.py` powers the Streamlit dashboard. This keeps responsibilities separate and makes the project easier to explain, test, and extend.

## Slide 5 — Strong Typing

Instead of using plain strings such as `"NUMBER"`, I used Python enums and frozen dataclasses. Each token carries its type, lexeme, semantic value, and exact source span. This matters because precise metadata is what enables diagnostics, dashboards, and future parser integration.

## Slide 6 — Lazy Evaluation

I also incorporated a very simple step-by-step explanation of the generator loop on the previous slide, making the code itself almost speak to the viewer.

One of the key engineering decisions is that the lexer uses `yield` to stream tokens. In other words, tokenization is lazy. The lexer does not need to build a giant list up front to do its core job. This mirrors how real compiler frontends and data pipelines often process large inputs incrementally.

## Slide 7 — Diagnostic Engine

Following the token model slide I inserted a Diagnostics slide that shows the caret output and explains why error messages are constructed the way they are.

The lexer has a custom `LexicalError` instead of falling back to a raw Python exception. If the user writes an illegal character like `@`, the system prints a line-and-column diagnostic with a caret pointer. This improves debuggability and also makes the demo much more professional.

## Slide 8 — Dashboard

To overachieve beyond the CLI, I built a Streamlit dashboard called TensorScript Observatory. It has an input studio, token metrics, an interactive token matrix, a syntax-colored source lens, a diagnostics panel, and an architecture tab that exposes the implementation itself. So the lexer is not only executable, but inspectable.

## Slide 9 — Verification

I validated the project with automated tests covering generator behavior, float parsing, integer parsing, token positions, comment toggling, syntax highlighting, and failure cases. I also smoke-tested the CLI and error reporting paths. That means the project is not only visually polished, but technically defended.

## Slide 10 — Conclusion

The final result is a lexer that satisfies the lab requirements while clearly exceeding them. It is domain-aware, strongly typed, memory-conscious, test-backed, and presentation-ready. In short, it looks and behaves more like a miniature compiler frontend than a typical classroom exercise.
