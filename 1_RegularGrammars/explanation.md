Read [](file:///d%3A/uni/year2/dsllab/1_RegularGrammars/src/grammar.py)

Read [](file:///d%3A/uni/year2/dsllab/1_RegularGrammars/src/automaton.py)

Read [](file:///d%3A/uni/year2/dsllab/1_RegularGrammars/config/variant_13.json)

Read [](file:///d%3A/uni/year2/dsllab/1_RegularGrammars/tests/test_pipeline.py)

Read [](file:///d%3A/uni/year2/dsllab/1_RegularGrammars/main.py)

Read [](file:///d%3A/uni/year2/dsllab/1_RegularGrammars/src/visualizer.py)

Read [](file:///d%3A/uni/year2/dsllab/1_RegularGrammars/requirements.txt)

## Quick summary — what you'll get
- A step‑by‑step, first‑principles explanation of the project, how to run it, and exactly where the key concepts live in the code.
- Short, copy‑ready lines you can paste into your report or present verbally.

---

## 1) How to run the code (step‑by‑step)
Prerequisites: Python 3.10+ and Git. From the project root (1_RegularGrammars):

1. Create and activate a virtual environment
   - PowerShell:
     - `python -m venv .venv`
     - `. .venv/Scripts/Activate.ps1`
2. Install dependencies
   - `pip install -r requirements.txt`
3. Run the CLI
   - Generate 5 strings: `python main.py --generate 5`
   - Validate a string: `python main.py --validate aac`
   - Visualize automaton: `python main.py --visualize`
   - Benchmark generation: `python main.py --benchmark 100`
4. Run tests
   - `pytest -q`

What each command does:
- `--generate N` builds the grammar and prints N sampled strings (each checked by the automaton).
- `--validate` runs the automaton on a single string and prints the state path.
- `--visualize` draws the automaton with NetworkX/Matplotlib.

---

## 2) Project entry points & where to look
- Grammar definition: variant_13.json
- Grammar implementation: grammar.py (`Grammar`, `Production`, `production_map`)
- Automaton implementation: automaton.py (`Automaton`, `check`, `check_with_path`)
- CLI and examples: main.py
- Visualizer: visualizer.py
- Tests: test_pipeline.py

---

## 3) From first principles — core concepts and how they map to code

What is a Markov chain?
- A process that moves between states where the next state depends only on the current state (memoryless).
- Relation to this project: sampling from a grammar is similar in spirit — the generator chooses a production based only on the current non‑terminal. If you add explicit probabilities to productions, the grammar generator becomes a Markov chain over non‑terminals.

What is a hash map?
- A data structure that maps keys to values with (average) O(1) lookup time.
- In Python, `dict` is a hash map.

What is `production_map` (in this code)?
- A hash map that groups productions by their source non‑terminal so the generator can quickly pick applicable productions.
- Location: grammar.py, attribute `Grammar.production_map`.

Concrete example (Variant 13):
- `production_map['B']` contains the productions `aD`, `bB`, `cS` (i.e., all rules that start from `B`).

Where to find and inspect it at runtime:
- Python quick check:
  - `python -c "from src.grammar import Grammar; g=Grammar('config/variant_13.json'); print(g.production_map)"`
  - That prints a dict keyed by non‑terminals.

---

## 4) How the Grammar generates strings (code → behavior)
- Core method: `Grammar.sample()` → calls `_recursively_sample(start)`.
- Process:
  1. Look up available productions for current non‑terminal via `production_map` (O(1)).
  2. Choose one production uniformly at random (`random.choice`).
  3. For each symbol in the production string:
     - if symbol is a non‑terminal → recurse and expand it
     - else → append terminal to output
  4. Return the concatenated terminal string.

Key code lines (conceptual):
- group productions: `self.production_map[prod.source_state].append(prod)`
- sampling loop: `chosen_production = random.choice(possible_productions)`

Why recursion?
- Because productions can expand to other non‑terminals; recursion fully expands each non‑terminal to terminals.

---

## 5) The Automaton — what it is and what it does
Formal definition (in plain words):
- A finite automaton has states, an input alphabet (terminals), a transition function, a start state, and accepting (final) states.
- It consumes an input string token by token and follows transitions; if it ends in an accepting state, the string is accepted.

Project specifics:
- `Grammar.build_finite_automaton()` converts grammar productions into transitions.
  - Productions `A -> aB` become transition `(A, 'a') -> B`.
  - Terminal-only productions `D -> c` become transitions to a virtual final state `Ω`.
- `Automaton` class stores:
  - `states`, `transitions` (dict keyed by `(state, token)`), `start_state`, `accepting_states`.

How the automaton checks a string:
- `Automaton.check(input_string)`:
  1. Set `current_state = start_state`.
  2. For each token in the string:
     - if `(current_state, token)` not in `transitions`, reject immediately.
     - else move to the mapped state.
  3. After all tokens, accept if `current_state` is in `accepting_states`.
- `check_with_path` returns the state path for debugging.

Where to read the code:
- grammar.py method `build_finite_automaton`
- automaton.py methods `check` and `check_with_path`

Example transition mapping (from Variant 13):
- `(S, 'a') -> B`
- `(D, 'c') -> Ω` (Ω is accepting)

---

## 6) How to explain/teach this to someone (short scripts)

Explaining the Grammar (one line)
- "The grammar defines how symbols expand; the program repeatedly replaces non‑terminals using the grammar rules until only terminals remain."

Explaining the Generator (one line)
- "Start at `S` and randomly pick applicable rules; expand recursively to produce a terminal string."

Explaining the Automaton (one line)
- "The automaton checks a string by following transitions for each input symbol; if it ends in the final state `Ω`, the string is valid."

Explaining production_map (one line)
- "A dictionary mapping each non‑terminal to its list of production rules so lookups are O(1)."

Suggested demo script (what to say while showing results)
1. "Load the grammar from variant_13.json."
2. "Generate a sample: `python main.py --generate 1` — here’s how the generator expanded each non‑terminal."
3. "Convert to automaton and validate the string with `python main.py --validate <string>`."
4. "Visualize the automaton with `python main.py --visualize` and point out `S`, loops, and `Ω`."

---

## 7) Useful short technical snippets you can paste in your report

How `production_map` is built (report snippet)
- `production_map: Dict[str, List[Production]] = { 'B': [Production('B','aD'), Production('B','bB'), ...], ... }`

How the automaton transition table looks
- `transitions = { ('S','a'): 'B', ('D','c'): 'Ω', ... }`

Generator complexity
- Sampling: time depends on output length; looking up productions is O(1) via `production_map`.

Automaton complexity
- Validation: O(n) in input length (single pass).

---

## 8) Where to change behavior / extend the project
- Add probabilities to productions in `config/*.json` and change `random.choice` → weighted choice to make it a true probabilistic Markov‑style generator.
- Add DFA minimization after `build_finite_automaton()` in grammar.py.
- Add unit tests in `tests/` to cover new behavior.

---

## 9) Quick examples (commands + expected output)
- `python main.py --generate 3`
  - prints 3 sampled strings and "Accepted"
- `python main.py --validate aac`
  - prints `String 'aac' -> Accepted` and the path `['S', 'B', 'D', 'Ω']`
- `pytest -q`
  - runs unit tests in test_pipeline.py

---

If you want, I can:
- produce a 1‑page handout with the exact wording for each report section,
- add inline comments in report.tex explaining each paragraph,
- or create short slides from the above script.

Which of those should I do next?
