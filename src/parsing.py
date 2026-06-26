import json
import sys
from typing import Literal, Annotated
from pydantic import BaseModel, StringConstraints, TypeAdapter
import pydantic


class ObjType(BaseModel):
    model_config = {"extra": "forbid"}
    type: Literal["number", "string", "boolean", "integer"]


non_empty = Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]


class FunctionDef(BaseModel):
    model_config = {"extra": "forbid"}
    name: non_empty
    description: non_empty
    parameters: dict[non_empty, ObjType]
    returns: ObjType


class InputPrompt(BaseModel):
    model_config = {"extra": "forbid"}
    prompt: non_empty


list_func_def = Annotated[list[FunctionDef], StringConstraints(min_length=1)]
list_input_prompt = Annotated[list[InputPrompt], StringConstraints(min_length=1)]


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
                if attr == "functions_definition":
                    adapter = TypeAdapter(list_func_def)
                else:
                    adapter = TypeAdapter(list_input_prompt)

                adapter.validate_json(data)
                setattr(self, attr + "_json", json.loads(data))
            if len(self.input_json) == 0:
                raise ValueError("No prompt are provided")

        except pydantic.ValidationError as e:
            print("File", f'"{path}"')
            print(f"Error: Json not valid")
            for error in e.errors():
                print(f"Field {error['loc']}: {error['msg']}")

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
