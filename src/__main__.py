from src.enums import QuotationState, State

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


# model.set_input_ids()
# model.write_json(State.START)
# print("fn_chil3ba", end="")
# model.write_json(State.PARAMETERS)


def generate_parameters():
    model.write_json(State.PARAMETERS)


# generate_parameters()


# model.set_input_ids("fn_add_numbers")

# model.write_token(numpy.argmax(model.generate_logits()))
# model.write_json(State.START)
# while True:
#     if state.current_state == State.FUN_NAME:
#         posible_functions, allowed_ids = state.get_allowed_func_ids()
#         token_id = 0
#         if len(posible_functions) == 1:
#             token_id = allowed_ids[0]
#         else:
#             token_id = state.get_correct_id(model.generate_logits(), allowed_ids)

#         state.update_state(token_id)
#         model.write_token(token_id)

#         if state.check_func_ids():
#             generate_parameters()
#             model.prompt_idx += 1
#             if model.prompt_idx >= len(model.prompts):
#                 model.write_json(State.END)
#                 break
#             model.write_json(State.PARAMETERS)
#             model.input_ids = []
#             model.set_input_ids()
#             state.old_chosen_ids = []
#             state.func_next_id_idx = 0

#     elif state.current_state == State.PARAMETERS:
