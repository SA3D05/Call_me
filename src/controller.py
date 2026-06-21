from pprint import pprint

from llm_sdk import Small_LLM_Model
from src.model import Model
from src.state_machine import StateMachine
from src.writer import Writer


class Controller:
    def __init__(
        self, func_def: list[dict], prompts: list[str], output_file: str
    ) -> None:

        self.functions = func_def
        self.prompts = prompts
        self.output_file = output_file

        self.model = Model(prompts, func_def)

        self.state_machine = StateMachine(self.model.model, func_def)
        self.writer = Writer(prompts, func_def)

        # pprint(self.__dict__)

    def start_generating(self) -> None:

        for p in self.prompts:

            current_func = self.__generate_func_name(p)
            # writer.build_context(func)
            self.__generate_arguments(current_func, p)

            # model.prompt_idx += 1
            # if model.prompt_idx >= len(model.prompts):
            #     break

            # writer.write_next_obj()
            # model.input_ids = []
            # model.set_input_ids()
            # state.old_chosen_func_ids = []
            # state.func_next_id_idx = 0

    def __get_func_parameters(self, target_func: str) -> dict[str, str]:
        result: dict[str, str] = {}
        for func in self.functions:
            if func["name"] == target_func:
                for param_name, param_type in func["parameters"].items():
                    result[param_name] = param_type["type"]
        return result

    def __generate_func_name(self, prompt: str) -> str:
        result: str = ""
        id_idx: int = 0

        print(f"{prompt}:", end=" ", flush=True)
        model = self.model
        model.set_func_input_ids(prompt)

        old_chosen_ids: list[int] = []
        functions = [f["name"] for f in self.functions]

        while result not in functions:
            logits = model.generate_logits()
            posible_functions, allowed_ids = self.state_machine.get_allowed_func_ids(
                id_idx, old_chosen_ids
            )
            if len(posible_functions) == 1:
                pass

            correct_id = self.state_machine.get_correct_func_id(logits, allowed_ids)
            old_chosen_ids.append(correct_id)
            id_idx += 1
            token = model.set_token_id(correct_id)
            result += token
            print(token, end="", flush=True)
        print()
        return result

    def __generate_arguments(self, target_func: str, prompt: str):

        parameters = self.__get_func_parameters(target_func)
        self.model.set_param_input_ids(target_func, prompt)
        is_first: bool = True
        for param_name, param_type in parameters.items():
            # self.writer.write_next_param()
            self.model.update_param_input_ids(is_first, param_name)
            is_first = False
            self.state_machine.params_end = False
            while not self.state_machine.params_end:

                correct_id = self.state_machine.write_correct_arg_id(
                    self.model.generate_logits(), param_type
                )
                self.model.input_ids.append(correct_id)
            print()
