from src.controller import Controller
from src.writer import Writer
from .state_machine import StateMachine
from .model import Model
from .parsing import GlobalInfo
import sys

if len(sys.argv) != 7:
    print("Error: arguments not correct")
    sys.exit()


info = GlobalInfo()

info.get_paths(sys.argv[1:])
info.get_json()
prompts_list = [prompt["prompt"] for prompt in info.input_json]

controller = Controller(info.functions_definition_json, prompts_list, info.output_path)
controller.start_generating()
sys.exit()
