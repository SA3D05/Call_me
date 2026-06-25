import json
import sys
from typing import Literal
from pydantic import BaseModel, TypeAdapter
import pydantic


class ObjType(BaseModel):
    type: Literal["number", "string"]


class FunctionDef(BaseModel):
    name: str
    description: str
    parameters: dict[str, ObjType]
    returns: ObjType


class InputPrompt(BaseModel):
    prompt: str


class GlobalInfo:
    def __init__(self):
        self.functions_definition_path: str = ""
        self.input_path: str = ""
        self.output_path: str = ""
        self.functions_definition_json: list[dict] = []
        self.input_json: list[dict] = []

    def get_paths(self, args: list[str]) -> None:
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

    def get_json(self) -> None:
        path = ""
        try:
            for attr in ["functions_definition", "input"]:
                path = getattr(self, attr + "_path")
                data = ""
                with open(path, "r") as f:
                    data = f.read()
                # if attr == "functions_definition":
                #     adapter = TypeAdapter(list[FunctionDef])
                # else:
                #     adapter = TypeAdapter(list[InputPrompt])

                # adapter.validate_json(data)
                setattr(self, attr + "_json", json.loads(data))
        except pydantic.ValidationError as e:
            print("File", f'"{path}"')
            print(f"Error: Json not valid")
            print(e)
            sys.exit()
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
