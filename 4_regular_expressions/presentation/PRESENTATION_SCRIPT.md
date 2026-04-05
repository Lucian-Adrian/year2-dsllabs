# Lab 4 Presentation Script

## Opening Strategy

This deck is built for live presenting. The slide content stays visual and compact; the detailed explanation lives here.

Recommended timing:

- 12 to 14 minutes for a clean delivery
- 15 to 18 minutes if the instructor interrupts with questions

Recommended rhythm:

- Part 1: problem and architecture
- Part 2: all-variant evidence
- Part 3: proof, reproducibility, and defense

## Slide-by-Slide Talking Points

### Slide 1 - Cover

- Open with the central claim: this is not a hardcoded generator.
- Say that the system parses, generates, validates, and explains regexes dynamically.
- Point to the four headline metrics as evidence of scope and engineering discipline.

### Slide 2 - Why This Lab Exists

- Define the problem in one sentence: interpret symbolic expressions into valid words.
- Frame regexes as compact programs, not just patterns for search.

### Slide 3 - Assignment Reality Check

- Explain the actual requirements from the brief.
- Mention the bonus requirement for processing sequence.
- Emphasize that all four variants were considered, not only one picture.

### Slide 4 - Wrong vs Correct Approach

- Say that hardcoding outputs would fail the spirit of the task.
- State that the correct engineering decision is to build a universal interpreter.

### Slide 5 - Explain It Like I’m Five

- Use the “recipe for legal strings” metaphor.
- Translate alternation, concatenation, star, plus, and exact power into plain language.

### Slide 6 - Formal Model

- Transition from intuition to structure.
- Explain that the engine uses a typed AST as the internal representation.

### Slide 7 - End-to-End Architecture

- Walk left to right through the pipeline.
- Stress the separation of parsing, generation, validation, and explainability.

### Slide 8 - Normalization

- Explain why handwritten notation is dangerous for raw parsing.
- Mention whitespace removal and superscript normalization.

### Slide 9 - Recursive-Descent Parsing

- Explain precedence in this exact order: repetition, concatenation, alternation.
- State that this is standard compiler-style syntax analysis.

### Slide 10 - Parser Strategy in Code

- Mention that `_parse_union`, `_parse_concat`, and `_parse_repetition` mirror the grammar.
- Stress that code structure follows language structure.

### Slide 11 - AST Example

- Use the tree to show how the expression becomes a compositional program.
- Explain each node type in the context of the example, not abstractly.

### Slide 12 - Deterministic Enumeration

- Say that deterministic mode is useful for repeatable evidence and debugging.
- Mention deduplication and output bounds.

### Slide 13 - Repeat Cap

- Explain that `*` and `+` describe infinite languages.
- The cap of 5 is required by the assignment and makes enumeration finite.

### Slide 14 - Random Trace Sampling

- Present this as the bonus-point feature.
- Explain that the trace tells us why a specific output appeared.

### Slide 15 - Independent Validation

- Stress the importance of a second line of evidence.
- Say the engine does not trust itself blindly; it cross-checks generated strings with Python regex.

### Slide 16 - Universal Variant Coverage

- State clearly that the engine is universal across all assignment variants.
- Use this as a transition into the evidence slides.

### Slide 17 - All Four Variants at a Glance

- Mention that the handwritten inputs differ visually and structurally.
- Stress that the pipeline handles them all without rewriting the algorithm.

### Slide 18 - Variant Map After Interpretation

- Explain that handwritten formulas were normalized into explicit regex strings.
- This is where ambiguity is resolved carefully but transparently.

### Slide 19 - Variant 1

- Highlight optional suffixes, plus repetition, and exact powers.
- Mention that Variant 1 already shows mixed operator behavior.

### Slide 20 - Variant 2

- Explain that exact counts make it structurally clean.
- Mention the balance between bounded repetition and optional growth.

### Slide 21 - Variant 3

- Call this the hardest case in the set.
- Mention the very large bounded search space and why it is a stress test.

### Slide 22 - Variant 4

- Explain why this variant is visually good for demos.
- Emphasize that the demo-friendliness does not mean variant-specific implementation.

### Slide 23 - Cross-Variant Metrics

- This is the strongest “analysis” slide.
- Mention nodes, depth, alternations, repeats, and rough paths.
- Point to Variant 3, Expression 3 as the most explosive example.

### Slide 24 - Why Complexity Grows Fast

- Explain combinatorial growth in plain language.
- Tie this directly to the repeat cap and bounded generation strategy.

### Slide 25 - Verification Strategy

- Mention parsing tests, sample validation, generation tests, and visualization checks.
- Say that the system is not only implemented but also verified.

### Slide 26 - Correctness Contract

- Use theorem-like language without sounding artificial.
- Stress the three trust layers: parse correctly, generate legally, validate independently.

### Slide 27 - Terminal Proof

- Show the real command used to generate the evidence bundle.
- Stress that the transcript, JSON summary, and markdown summary are generated artifacts, not manually written text.

### Slide 28 - Reproducibility Pack

- Explain that the project is reproducible, not just presentable.
- Point to the exact commands needed to regenerate evidence and rebuild the artifacts.

### Slide 29 - Benchmark Evidence

- Explain that parsing stays cheap while generation reflects structural complexity.
- Point to the heavier cases and connect them back to alternation plus repetition.

### Slide 30 - Quantitative Outliers

- Use this slide to sound like an analyst.
- Point out that Variant 3, Expression 3 dominates the bounded search proxy by a large margin.
- Connect the outliers back to combinatorics, not implementation slowness.

### Slide 31 - Example Trace

- Walk through the trace line by line.
- Say this is the clearest answer to the bonus requirement.

### Slide 32 - ML Analogy

- Present the analogy carefully.
- Emphasize that ASTs act like symbolic constraints and validation acts like a hard checker.
- Make clear this is pedagogical framing, not a confusion of domains.

### Slide 33 - Real Engineering Difficulties

- Mention ambiguity in the handwritten brief, infinite repetition, and explainability.
- Then pivot: the final result is stronger because those problems were solved explicitly.

### Slide 34 - How I Would Demo It Live

- Explain that the live demo is intentionally short and evidence-driven.
- Show one universal run, one trace run, and one test run.

### Slide 35 - Hard Questions, Short Answers

- Treat this as a reserve slide.
- If no one asks hard questions, skip it.
- If challenged, answer in one sentence first and only expand if needed.

### Slide 36 - Conclusion

- End with the line that this is a small formal-language engine, not a toy script.
- Reiterate the four properties: universal, bounded, verified, explainable.

## Suggested Demo Commands

```powershell
python 4_regular_expressions/main.py --variant all --samples 8 --validate
python 4_regular_expressions/main.py --variant 4 --samples 10 --show-steps --validate
python -m pytest 4_regular_expressions/tests -q
```

## Likely Questions and Strong Answers

### Why not hardcode per variant?

Because the assignment explicitly asks for dynamic interpretation of given regexes. Hardcoding would produce outputs, but not a general solution.

### Why cap repetition at 5?

Because `*` and `+` define potentially infinite languages, while the assignment requires finite generation. The cap keeps enumeration tractable and matches the stated rule.

### How do you know the generated words are correct?

The engine uses an independent validator by converting the AST into a Python-compatible regex and checking every generated candidate with `fullmatch`.

### What is the hardest expression?

Variant 3, Expression 3, because it combines mandatory repetition, optional segments, branching, and exact suffix repetition, giving the largest bounded search space in the analysis.

### What is the bonus feature?

The trace system. It shows the internal sequence of branch choices and repetition counts that produced one generated word.

### What is new beyond the minimum lab requirement?

The evidence bundle, cross-variant metrics, benchmark interpretation, reproducibility workflow, and the presentation/report package that treats the lab like a small research artifact instead of a one-off script.
