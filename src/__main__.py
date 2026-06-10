from enum import Enum
from pprint import pprint
import sys
import json

if len(sys.argv) != 7:
    print("Error: arguments not correct")
    sys.exit()


class GlobalInfo:
    def __init__(self):
        self.functions_definition_path: str = ""
        self.input_path: str = ""
        self.output_path: str = ""

        self.functions_definition_json: dict = {}
        self.input_json: dict = {}

    def get_paths(self, args: list[str]):
        try:
            for flag in ["--functions_definition", "--input", "--output"]:
                attr = flag.lstrip("-") + "_path"

                try:
                    flag_idx = args.index(flag)
                except ValueError:
                    raise ValueError(f"missing a required flag '{flag}'")

                try:
                    value = args[flag_idx + 1]
                except IndexError:
                    raise ValueError(f"missing value for flag '{flag}'")

                if not value.endswith(".json"):
                    raise ValueError(f"invalid value for flag '{flag}'")

                setattr(self, attr, value)
        except ValueError as e:
            print("Error:", e)
            sys.exit()

    def get_json(self):
        path = ""
        try:
            for attr in ["functions_definition", "input"]:
                path = getattr(self, attr + "_path")
                data = ""
                with open(path, "r") as f:
                    data = f.read()

                setattr(self, attr + "_json", json.loads(data))

        except OSError as e:
            print("File", f'"{path}"')
            print(f"Error: {e.strerror}")
            sys.exit()

        except json.decoder.JSONDecodeError as e:
            print("File", f'"{path}"')
            print(f"Error: {e}")
            sys.exit()

        except Exception as e:
            print("File", f'"{path}"')
            print(f"Error: {e}")
            sys.exit()


info = GlobalInfo()

info.get_paths(sys.argv[1:])
info.get_json()
pprint(info.__dict__)
