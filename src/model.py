import sys

# Disable Hugging Face progress bars
import os

os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"


import numpy

from llm_sdk import Small_LLM_Model
from src.enums import State


class Model:
    def __init__(self, prompts: list, functions: list):
        self.model = Small_LLM_Model()
        self.prompts = prompts
        self.functions = functions
        self.func_idx = 0

        self.prompt_idx: int = 0
        self.input_ids: list[int] = []
        self.indent_level = 4
        self.param_idx = 0
        self.params_names = []

    def __set_func_params(self, target_func: str):

        for func in self.functions:
            if func["name"] == target_func:
                for param in func["parameters"].keys():
                    self.params_names.append(param)

    def get_func_info(self, target_func: str = "") -> str:
        result = ""
        for func in self.functions:
            if target_func != "" and func["name"] != target_func:
                continue
            first = True
            result += func["name"] + "("
            for param_name, param_type in func["parameters"].items():
                result += ", " if not first else ""
                result += param_name + ": " + param_type["type"]
                first = False
            result += "), description: " + func["description"] + "\n"
        return result

    def set_input_ids(self, target_func: str = ""):
        prompt = ""
        function_info = self.get_func_info(target_func)
        self.__set_func_params(target_func)

        if target_func != "":
            prompt = (
                "You are a function parameters extractor agent,"
                + " your goal is to extract the arguments for the function: "
                + f"'{target_func}'"
                + " from the user query."
                + "\nseperate the aruments by newline"
                + "\n\nfunction:\n"
                + function_info
                + f"\n\nuser query:\n'{self.prompts[self.prompt_idx]}'"
                + "\n\nanswer:\n"
            )

        else:
            prompt = (
                "You are a function selector agent,"
                + " your goal is to select the correct"
                + " function name based on the user query."
                + "\n\nfunctions:\n"
                + function_info
                + "\nuser query:\n"
                + f'"{self.prompts[self.prompt_idx]}"'
                + "\n\nanswer:\n"
                + "fn_"
            )
        ids = self.model.encode(prompt).tolist()[0]
        self.input_ids.extend(ids)

    def update_param_input_ids(self):

        param: str = self.params_names[self.param_idx]
        prompt = ""

        if self.param_idx > 0:
            prompt += '", '

        prompt += f'"{param}":"'

        self.param_idx += 1
        ids: list[int] = self.model.encode(prompt).tolist()[0]
        self.input_ids.extend(ids)

    def generate_logits(self) -> list[float]:
        logits = self.model.get_logits_from_input_ids(self.input_ids)

        return logits

    def write_token(self, token_id: int):
        self.input_ids.append(token_id)
        print(self.model.decode([token_id]), end="")
