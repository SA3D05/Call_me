from enum import Enum
from pprint import pprint
import sys

if len(sys.argv) != 7:
    print("Error: arguments not correct")
    sys.exit()


class GlobalInfo:
    def __init__(self):
        self.functions_definition_path = ""
        self.output_path = ""
        self.prompts_path = ""

    def get_paths(
        self,
    ):
        try:
            pass
        except Exception as e:
            print("Error:", e)
            sys.exit()


info = GlobalInfo()


args = sys.argv
args.pop(0)


info.functions_definition_path = args[args.index("--functions_definition") + 1]

if not info.functions_definition_path.endswith(".json"):
    print("Error: functions_definition_path not correct")
    sys.exit()

info.output_path = args[args.index("--output") + 1]
info.prompts_path = args[args.index("--input") + 1]


pprint(info.__dict__)
