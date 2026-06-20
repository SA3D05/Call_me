from time import sleep

from src.enums import ArgType, State
from src.writer import Writer

from .state_machine import StateMachine

from .model import Model
from .parsing import GlobalInfo
from pprint import pprint
import sys
import numpy

if len(sys.argv) != 7:
    print("Error: arguments not correct")
    sys.exit()


info = GlobalInfo()


info.get_paths(sys.argv[1:])
info.get_json()
prompts_list = [prompt["prompt"] for prompt in info.input_json]
model = Model(
    prompts_list,
    info.functions_definition_json,
)


state = StateMachine(model.model, info.functions_definition_json)
writer = Writer(prompts_list, info.functions_definition_json)


def get_func_params(target_func: str) -> dict[str, ArgType]:
    result: dict[str, ArgType] = {}
    for func in info.functions_definition_json:
        if func["name"] == target_func:
            for param_name, param_type in func["parameters"].items():
                result[param_name] = (
                    ArgType.NUMBER if param_type["type"] == "number" else ArgType.STRING
                )
    return result


def generate_arguments(target_func: str):

    parameters = get_func_params(target_func)
    model.set_input_ids(target_func)

    for param_type in parameters.values():
        writer.write_next_param()
        model.update_param_input_ids()
        state.params_end = False
        while not state.params_end:

            correct_id = state.write_correct_arg_id(model.generate_logits(), param_type)
            model.input_ids.append(correct_id)


def generate_func():
    while True:
        posible_functions, allowed_ids = state.get_allowed_func_ids()
        token_id = 0

        if len(posible_functions) == 1:
            token_id = allowed_ids[0]
        else:
            token_id = state.get_correct_func_id(model.generate_logits(), allowed_ids)

        state.update_state(token_id)
        model.write_token(token_id)
        if state.check_func_ids():
            return


prompt_idx = 0
writer.write_next_obj()
model.set_input_ids()


for _ in prompts_list:

    generate_func()
    func: str = state.current_func if state.current_func else ""
    writer.build_context(func)
    generate_arguments(func)

    model.prompt_idx += 1
    if model.prompt_idx >= len(model.prompts):
        break

    writer.write_next_obj()
    model.input_ids = []
    model.set_input_ids()
    state.old_chosen_func_ids = []
    state.func_next_id_idx = 0


# writer.write_end()
# with open(info.output_path, "w") as f:
#     f.write(writer.result)
