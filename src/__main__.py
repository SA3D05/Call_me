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


def get_func_params(target_func: str):
    result: list[str] = []
    for func in info.functions_definition_json:
        if func["name"] == target_func:
            for param in func["parameters"].keys():
                result.append(param)

    return result


def generate_arguments(target_func: str):

    parameters = get_func_params(target_func)
    model.set_input_ids(target_func)

    for param in parameters:

        writer.write_json(State.PARAMETERS, param)
        state.params_end = False
        while not state.params_end:

            correct_id = state.write_correct_arg_id(
                model.generate_logits(), ArgType.NUMBER
            )
            model.input_ids.append(correct_id)

        model.update_param_input_ids()


# generate_parameters()


# try:
#     while True:
#         model.write_token(numpy.argmax(model.generate_logits()))  # type: ignore
# except BaseException:
#     pass


# model.set_input_ids()

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
        generate_arguments(state.current_func)
        model.prompt_idx += 1
        if model.prompt_idx >= len(model.prompts):
            writer.write_json(State.END)
            break
        writer.write_json(State.FUN_NAME)
        model.input_ids = []
        model.set_input_ids()
        state.old_chosen_func_ids = []
        state.func_next_id_idx = 0

#     elif state.current_state == State.PARAMETERS:
