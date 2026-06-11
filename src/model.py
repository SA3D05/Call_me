from llm_sdk import Small_LLM_Model


class Model:
    def __init__(self, prompts: list, functions: list):
        self.model = Small_LLM_Model()
        self.prompts = prompts
        self.functions = functions
        self.prompt_idx: int = 0
        self.input_ids = []

    def get_prompt(self):
        return f"""You are a function-calling assistant.

Your task is to select the most appropriate function and generate its arguments.

Available functions:

{self.functions}

User request:

{self.prompts[self.prompt_idx]}

Rules:
1. Return ONLY valid JSON.
2. Do not write explanations.
3. Do not write markdown.
4. Do not write code fences.
5. The output must be a JSON object.
6. Use exactly one function.
7. The function name must come from the available functions.
8. Arguments must match the function schema.
9. If a value is not explicitly provided, infer it only when reasonable.
10. Do not invent parameters that are not in the schema.

Output format:

{{
  "name": "<function_name>",
  "parameters": {{
    ...
  }}
}}
"""

    def generate(self):
        self.input_ids.extend(self.model.encode(self.get_prompt()).tolist()[0])
        logits = self.model.get_logits_from_input_ids(self.input_ids)
        return logits
