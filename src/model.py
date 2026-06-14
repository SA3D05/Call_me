import numpy

from llm_sdk import Small_LLM_Model


class Model:
    def __init__(self, prompts: list, functions: list):
        self.model = Small_LLM_Model()
        self.prompts = prompts
        self.functions = functions
        self.prompt_idx: int = 0
        self.input_ids: list[int] = []

    def set_input_ids(self):
        fn = "\n".join(
            f"name: '{func['name']}', description: '{func['description']}'"
            for func in self.functions
        )

        # message = "Name: %s | Age: %d | Height: %.2f m" % (name, age, height)
        prompt = (
            "You are a function selector agent,"
            + " your goal is to select the correct"
            + " function name based on the user query."
            + "\n\nfunctions:\n"
            + fn
            + f"\n\nuser query:\n'{self.prompts[self.prompt_idx]}'"
            + "\n\nanswer:\n"
        )
        print(prompt)
        ids = self.model.encode(prompt).tolist()[0]
        self.input_ids.extend(ids)

    def generate_logits(self) -> list[float]:
        logits = self.model.get_logits_from_input_ids(self.input_ids)

        return logits

    def write_token(self, token_id: int):
        self.input_ids.append(token_id)
        print(self.model.decode([token_id]), end="")
