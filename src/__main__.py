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
state = StateMachine(model.model, info.functions_definition_json, len(prompts_list))

indent_level = 4

model.set_input_ids()

for _ in range(3):
    posible_functions, allowed_ids = state.get_allowed_ids()
    token_id = 0
    if len(posible_functions) == 1:
        token_id = allowed_ids[0]
    else:
        token_id = state.get_correct_id(model.generate_logits(), allowed_ids)

    state.update_state(token_id)
    model.write_token(token_id)
print()
# def get_indent(value: int):
#     return "\n" + (" " * indent_level * value)


# if state.get_state() == State.START:
#     print("[", get_indent(1), "{", get_indent(2), '"', sep="")

# state.current_state = State.QUOTATION_MARK
# state.quotation_state = QuotationState.PROMPT_NAME_END
# state.update_state()
# model.generate()
