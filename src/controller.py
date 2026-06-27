import sys

from .model import Model
from .state_machine import StateMachine
from .writer import Writer


class Controller:
    """Controll function selection, argument generation, and output writing."""

    def __init__(
        self, func_def: list[dict], prompts: list[str], output_file: str
    ) -> None:
        """Initialize the controller.

        Args:
            func_def: Function definitions used to constrain generation.
            prompts: User prompts to convert into function calls.
            output_file: Path where the generated JSON output is written.
        """

        self.functions = func_def
        self.prompts = prompts
        self.output_file = output_file

        self.model = Model(prompts, func_def)

        self.state_machine = StateMachine(self.model.model, func_def)
        self.writer = Writer(prompts, func_def)

    def start_generating(self) -> None:
        """Generate all function calls and write them to the output file."""

        for prompt in self.prompts:

            self.writer.write_next_obj()
            current_func = self.__generate_func_name(prompt)
            self.writer.result += current_func
            self.__generate_arguments(current_func, prompt)

        self.writer.write_json_end()
        try:
            with open(self.output_file, "w") as f:
                f.write(self.writer.result)
        except OSError as e:
            print("File", f'"{self.output_file}"')
            print(f"Error: {e.strerror}")
            sys.exit()

    def __get_func_parameters(self, target_func: str) -> dict[str, str]:
        """Return the parameter types for a selected function.

        Args:
            target_func: Function name to inspect.

        Returns:
            A mapping of parameter names to their declared types.
        """

        result: dict[str, str] = {}
        for func in self.functions:
            if func["name"] == target_func:
                for param_name, param_type in func["parameters"].items():
                    result[param_name] = param_type["type"]
        return result

    def __generate_func_name(self, prompt: str) -> str:
        """Generate the function name that best matches a prompt.

        Args:
            prompt: The natural language prompt to classify.

        Returns:
            The generated function name.
        """

        result: str = ""
        id_idx: int = 0

        model = self.model
        model.set_func_input_ids(prompt)

        old_chosen_ids: list[int] = []
        functions = [f["name"] for f in self.functions]

        while result not in functions:
            logits = model.generate_logits()
            posible_functions, allowed_ids = (
                self.state_machine.get_allowed_func_ids(
                    id_idx,
                    old_chosen_ids,
                )
            )
            if len(posible_functions) == 1:
                pass

            correct_id = self.state_machine.get_correct_func_id(
                logits,
                allowed_ids,
            )
            old_chosen_ids.append(correct_id)
            id_idx += 1
            token = model.set_token_id(correct_id)
            result += token
            print(token, end="", flush=True)
        return result

    def __generate_arguments(self, target_func: str, prompt: str) -> None:
        """Generate argument values for the selected function.

        Args:
            target_func: Function name whose arguments are generated.
            prompt: The user prompt used as generation context.
        """

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
