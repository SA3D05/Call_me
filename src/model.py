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
        self.func_param_idx = 0
        self.parameter_write = False

    def __get_func_params(self, target_func: str):
        result = []
        for func in self.functions:
            if func["name"] == target_func:
                for param in func["parameters"].keys():
                    result.append(param)

        return result

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
        parameters = self.__get_func_params(target_func)

        if target_func != "":
            prompt = (
                "You are a function parameters extractor agent,"
                + " your goal is to extract the arguments for the function: "
                + f"'{target_func}'"
                + " from the user query."
                + "\nseperate the aruments by ','"
                + "\n\nfunction:\n"
                + function_info
                + f"\n\nuser query:\n'{self.prompts[self.prompt_idx]}'"
                + "\n\nanswer:\n"
                + f'"{parameters[0]}":"'
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
            )
        print(prompt, end="")
        ids = self.model.encode(prompt).tolist()[0]
        self.input_ids.extend(ids)

    def generate_logits(self) -> list[float]:
        logits = self.model.get_logits_from_input_ids(self.input_ids)

        return logits

    def write_token(self, token_id: int):
        self.input_ids.append(token_id)
        print(self.model.decode([token_id]), end="")

    def get_indent(self, value: int):
        return "\n" + (" " * self.indent_level * value)

    def __write_prompt(self):
        print(
            self.get_indent(2),
            '"prompt":"',
            self.prompts[self.prompt_idx],
            '",',
            sep="",
            end="",
        )

    def __write_name(self):
        print(
            self.get_indent(2),
            '"name":"',
            sep="",
            end="",
        )

    def __write_start(self):
        print(
            "[",
            self.get_indent(1),
            "{",
            sep="",
            end="",
        )

    def __write_midd(self):
        print(
            '"',
            self.get_indent(1),
            "},",
            self.get_indent(1),
            "{",
            sep="",
            end="",
        )

    def __write_param(self):

        param_name = list(self.functions[self.func_idx]["parameters"].keys())[
            self.func_param_idx
        ]

        print(
            self.get_indent(3),
            f'"{param_name}":',
            end="",
            sep="",
        )

    def write_param_end(self):

        param_name = list(self.functions[self.func_idx]["parameters"].keys())[
            self.func_param_idx
        ]
        print(
            f'",',
            self.get_indent(3),
            f'"{param_name}":',
            end="",
            sep="",
        )

    def __write_parameters(self):
        print(
            '",',
            self.get_indent(2),
            '"parameters":{',
            end="",
            sep="",
        )

    def write_json(self, state: State):
        if state == State.START:
            self.__write_start()
            self.__write_prompt()
            self.__write_name()
        elif state == State.FUN_NAME:
            self.__write_midd()

        elif state == State.PARAMETERS:
            if not self.parameter_write:
                self.__write_parameters()
                self.parameter_write = True
            if self.func_param_idx < len(self.functions[self.func_idx]["parameters"]):
                self.__write_param()
                self.func_param_idx += 1

        elif state == State.END:
            print('"', self.get_indent(1), "}\n", "]")
