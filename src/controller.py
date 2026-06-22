from .model import Model
from .state_machine import StateMachine
from .writer import Writer


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

    def start_generating(self) -> None:

        for p in self.prompts:

            self.writer.write_next_obj()
            current_func = self.__generate_func_name(p)
            self.writer.result += current_func
            self.__generate_arguments(current_func, p)

        self.writer.write_end()
        with open(self.output_file, "w") as f:
            f.write(self.writer.result)

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
        return result

    def __generate_arguments(self, target_func: str, prompt: str):

        self.writer.build_context(target_func)
        parameters = self.__get_func_parameters(target_func)
        self.model.set_param_input_ids(target_func, prompt)
        is_first: bool = True

        for param_name, param_type in parameters.items():
            self.writer.write_next_param()
            self.model.update_param_input_ids(is_first, param_name)
            is_first = False
            self.state_machine.params_end = False

            while not self.state_machine.params_end:

                correct_id, result = self.state_machine.get_correct_arg(
                    self.model.generate_logits(), param_type
                )
                self.writer.result += result
                print(result, end="", flush=True)
                self.model.input_ids.append(correct_id)
