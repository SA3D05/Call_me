*This project has been created as part of the 42 curriculum by satifi.*

# Call Me Maybe

## Description

Call Me is a function-calling generator built around a constrained decoding pipeline. The project reads a list of function definitions and a list of user prompts, then produces a JSON file that maps each prompt to it correct function call and its extracted arguments.

The goal is to transform natural-language prompts into structured function calls while keeping the generated output valid and consistent with the available function schema. The implementation uses a local language model wrapper, a state machine that constrains token choices, and a streaming writer that assembles the final JSON output incrementally.

## Instructions

### Requirements

- Python 3.10 or newer
- `uv`
- A working environment for `torch`, `transformers`, `huggingface-hub`, `pydantic`, and `numpy`

### Installation

```bash
make install
```

The repository already includes the input fixtures expected by the program:

- `data/input/functions_definition.json`
- `data/input/function_calling_tests.json`

The generated result is written to:

- `data/output/function_calls.json`

### Execution

Run the generator with the provided Makefile target:

```bash
make run
```

Equivalent direct command:

```bash
uv run python -m src --functions_definition data/input/functions_definition.json --input data/input/function_calling_tests.json --output data/output/function_calls.json
```


## Algorithm Explanation

The core of the solution is constrained decoding. Instead of letting the language model freely generate arbitrary text, the program narrows each generation step to the set of tokens that can still lead to a valid function call.

The process works in two stages:

1. Function selection
   - The prompt is encoded with all available function definitions.
   - The model predicts token logits for the function name.
   - The state machine encodes every function name into token IDs and masks out invalid next tokens.
   - At each step, only token IDs that match at least one still-valid function prefix are considered.
   - Decoding stops once a full function name has been selected.

2. Argument generation
   - After the function name is chosen, the program builds a prompt for argument extraction.
   - Parameters are emitted in the function-defined order.
   - The writer streams a JSON structure while the model generates each parameter value.
   - The decoder treats string and number parameters differently so the output stays valid and quoted correctly when needed.

This design keeps the model from drifting into unrelated text and makes the output predictable enough to serialize directly into JSON.

## Design Decisions

- The project separates orchestration, decoding, and output formatting into `Controller`, `StateMachine`, `Model`, and `Writer` classes. That makes the constrained-decoding logic easier to reason about and test independently.
- Function definitions are validated with `pydantic` before decoding starts, which prevents malformed input schemas from affecting generation.
- The output is streamed rather than built as a Python object. This keeps the code close to the intended JSON layout and avoids a second serialization pass.
- The function name and parameter prompts are deliberately different. Function selection is optimized for classification, while argument generation is optimized for extraction.
- The state machine is responsible for constraints. The model proposes tokens, but the state machine decides what is legal at each step.

## Performance Analysis

Accuracy depends mainly on two factors: how well the model maps prompts to the right function name, and how reliably it extracts the correct argument values. The constrained decoder improves structural accuracy because invalid function names and malformed token sequences are rejected early.

Speed is acceptable for a small function catalog, but generation is sequential and token-by-token, so runtime grows with the number of prompts, function names, and parameter tokens. The use of a local model also means inference cost is higher than a simple rule-based parser.

Reliability is strongest on JSON validity and schema adherence. The decoder strongly reduces malformed output, but semantic accuracy still depends on the underlying model and the clarity of the prompt text. In practice, the approach is more reliable than unconstrained generation for structured function calling, especially when the function set is small and fixed.

## Challenges Faced

- Keeping the generated output valid JSON while still decoding incrementally required the writer to manage commas, quotes, braces, and parameter ordering carefully.
- Matching function names at token level was tricky because the model must only be allowed to continue with tokens that still match at least one valid function prefix.
- Numeric parameters needed special handling so values such as integers and decimals would be emitted consistently.
- The project input validation had to avoid rejecting the output path too early, while still ensuring the input files exist and the JSON schemas are correct.

These issues were solved by splitting validation across the parser, constraining token IDs with the state machine, and keeping output formatting in a dedicated writer.

## Testing Strategy

Validation for this project focused on a few complementary layers:

- Command-line smoke tests using different function-definition files and prompt sets
- Schema validation of the input JSON through `pydantic`
- JSON edge cases covering empty fields, missing keys, unexpected types, nested structures, and output-path handling

The repository fixtures in `data/input/` are useful for confirming that the program can read multiple input combinations and still produce a valid JSON output file in `data/output/`.

## Example Usage

Run the generator with the sample files included in the repository:

```bash
make run
```

While the program runs, it streams the generated structure to the terminal. When execution finishes, the final JSON file is available at `data/output/function_calls.json`.



## Example I/O

the input prompt:

```json
[
  {
    "prompt": "What is the sum of 2 and 3?"
  }
]
```
the output function calls:

```json
[
    {
        "prompt":"What is the sum of 2 and 3?",
        "name":"fn_add_numbers",
        "parameters":{
            "a": 2.0,
            "b": 3.0
        }
    }
]
```

You can inspect the result with:

```bash
cat data/output/function_calls.json
```

is converted into a structured function-call result based on the available definitions in `data/input/functions_definition.json`.

## Resources

Classic references and documentation:

- [A 3D animated visualization of an LLM by (Brendan Bycroft)](https://bbycroft.net/llm)
- [Deep Dive into LLMs by (Andrej Karpathy)](https://www.youtube.com/watch?v=7xTGNNLPyMI&t=3453s&pp=ygULZXhwbGFpbiBsbG0%3D)
- [A visually animated playlist covering the step-by-step how Large Language Models by (3Blue1Brown)](https://www.youtube.com/playlist?list=PLZHQObOWTQDM4E-dwvbnQTiyKDO-y9T2t)
- [I Visualised Attention in Transformersn by (Gal Lahat)](https://youtu.be/RNF0FvRjGZk)

- [A Guide to Structured Generation Using Constrained Decoding by (Aidan Cooper)](https://www.aidancooper.co.uk/constrained-decoding/)



AI was used to:

- Documenting code (README and docstrings).
- Exploring deep LLM concepts and constrained generation mechanics.