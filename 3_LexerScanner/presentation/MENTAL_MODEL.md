# TensorScript Mental Model

## One-Sentence Model

TensorScript Observatory is a lexical analysis workstation: it takes unstructured source code and turns it into a structured token dataset that can be inspected like an ML preprocessing pipeline.

## Conceptual Layers

1. Source Layer
   TensorScript code enters from a sample program, manual editor input, CLI argument, or uploaded file.

2. Scanner Layer
   The lazy lexer reads characters one-by-one and emits immutable token objects.

3. Classification Layer
   Each token is categorized into a specific token type and family: keyword, identifier, number, function, symbol, comment, or EOF.

4. Diagnostic Layer
   When the input is malformed, the pipeline returns a structured `LexicalError` with location and a repair-oriented pointer message.

5. Visualization Layer
   The CLI and Streamlit dashboard transform the raw token stream into tables, charts, summaries, and syntax-highlighted source.

## What To Emphasize During Presentation

* This is not a calculator.
* The lexer is strongly typed.
* The generator architecture supports streaming.
* Diagnostics are exact and user-friendly.
* The dashboard makes the frontend explainable.
* Tests prove the engineering claim.
