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

# model.set_input_ids()
# model.write_json(State.START)
# print("fn_chil3ba", end="")
# model.write_json(State.PARAMETERS)


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
    arg_start = True

    for param_name, param_type in parameters.items():
        arg_start = True
        model.update_param_input_ids()
        writer.write_json(State.PARAMETERS, param_name)
        state.params_end = False
        while not state.params_end:

            correct_id = state.write_correct_arg_id(
                model.generate_logits(), param_type, arg_start
            )
            model.input_ids.append(correct_id)
            arg_start = False


generate_arguments("fn_substitute_string_with_regex")
sys.exit()

writer.write_json(State.START)
model.set_input_ids()
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
        generate_arguments(state.current_func)  # type: ignore
        model.prompt_idx += 1
        writer.prompt_idx += 1
        if model.prompt_idx >= len(model.prompts):
            writer.write_json(State.END)
            break
        writer.write_json(State.FUN_NAME)
        model.input_ids = []
        model.set_input_ids()
        state.old_chosen_func_ids = []
        state.func_next_id_idx = 0

#     elif state.current_state == State.PARAMETERS:
