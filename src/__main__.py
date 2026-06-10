from enum import Enum
from pprint import pprint
import sys
import json

from llm_sdk import Small_LLM_Model

if len(sys.argv) != 7:
    print("Error: arguments not correct")
    sys.exit()


class GlobalInfo:
    def __init__(self):
        self.functions_definition_path: str = ""
        self.input_path: str = ""
        self.output_path: str = ""

        self.functions_definition_json: dict = {}
        self.input_json: dict = {}

    def get_paths(self, args: list[str]):
        try:
            for flag in ["--functions_definition", "--input", "--output"]:
                attr = flag.lstrip("-") + "_path"

                try:
                    flag_idx = args.index(flag)
                except ValueError:
                    raise ValueError(f"missing a required flag '{flag}'")

                try:
                    value = args[flag_idx + 1]
                except IndexError:
                    raise ValueError(f"missing value for flag '{flag}'")

                if not value.endswith(".json"):
                    raise ValueError(f"invalid value for flag '{flag}'")

                setattr(self, attr, value)
        except ValueError as e:
            print("Error:", e)
            sys.exit()

    def get_json(self):
        path = ""
        try:
            for attr in ["functions_definition", "input"]:
                path = getattr(self, attr + "_path")
                data = ""
                with open(path, "r") as f:
                    data = f.read()

                setattr(self, attr + "_json", json.loads(data))

        except OSError as e:
            print("File", f'"{path}"')
            print(f"Error: {e.strerror}")
            sys.exit()

        except json.decoder.JSONDecodeError as e:
            print("File", f'"{path}"')
            print(f"Error: {e}")
            sys.exit()

        except Exception as e:
            print("File", f'"{path}"')
            print(f"Error: {e}")
            sys.exit()


info = GlobalInfo()

info.get_paths(sys.argv[1:])
info.get_json()


model = Small_LLM_Model()

prompt_idx = 0

func_examples = """
[
{
"name": "fn_add_numbers",
"description": "Add two numbers",
"parameters": {
"a": {"type": "number"},
"b": {"type": "number"}
}
},
{
"name": "fn_reverse_string",
"description": "Reverse a string",
"parameters": {
"s": {"type": "string"}
}
}
]"""

expected_output_example = """[
{
"prompt": "What is the sum of 2 and 3?",
"name": "fn_add_numbers",
"parameters": {
"a": 2.0,
"b": 3.0
}
},
{
"prompt": "Reverse the string 'hello'",
"name": "fn_reverse_string",
"parameters": {
"s": "hello"
}
}
]"""

prompt_exaples = """[
{"prompt": "What is the sum of 2 and 3?"},
{"prompt": "Reverse the string 'hello'"}
]"""
prompt = f"""You are a function calling engine.

Your task is to convert natural language requests into function calls.

You are given:

1. A list of available functions.
2. A list of user prompts.

For each prompt:

- Choose the single best matching function.
- Extract all required parameters.
- Convert parameter values to the correct types.
- Do NOT execute the function.
- Do NOT explain your reasoning.
- Do NOT add comments.
- Do NOT add markdown.
- Return ONLY valid JSON.

The output MUST be a JSON array.

Each item MUST have exactly these keys:

- prompt
- name
- parameters

Available Functions:

{info.functions_definition_json}

User Prompts:

{info.input_json}

Output JSON:
"""

# try:
input_ids = model.encode(prompt).tolist()[0]
allowed = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_{}[],'\":\n\t\v "
allowed_ids = []
for i in ["_", "{", "}", "[", "]", ",", "'", '"']:
    allowed_ids.extend(model.encode(i).tolist()[0])

while True:
    logits = model.get_logits_from_input_ids(input_ids)
    next_id = logits.index(max(logits))
    a = model.decode([next_id])
    ok = False
    while not ok:
        ok = True
        for c in a:
            if c not in allowed:
                logits[next_id] = float("-inf")
                next_id = logits.index(max(logits))
                a = model.decode([next_id])
                ok = False
                break

    input_ids.append(next_id)
    print(model.decode([next_id]), end="", flush=True)
# except BaseException as e:
#     print(e)
#     sys.exit()
