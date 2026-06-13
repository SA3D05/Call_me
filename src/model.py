import numpy

from llm_sdk import Small_LLM_Model


class Model:
    def __init__(self, prompts: list, functions: list):
        self.model = Small_LLM_Model()
        self.prompts = prompts
        self.functions = functions
        self.prompt_idx: int = 0
        self.input_ids: list[int] = []

    def get_prompt(self):
        return f"""the capital of Morroco is """

    def generate(self) -> list[float]:
        ids: list[int] = self.model.encode(self.get_prompt()).tolist()[0]
        self.input_ids.extend(ids)
        logits = self.model.get_logits_from_input_ids(self.input_ids)

        return logits
