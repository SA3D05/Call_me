from typing import Literal

from pydantic import BaseModel, TypeAdapter

js = ""
with open("data/input/functions_definition.json", "r") as f:
    js = f.read()


class ObjType(BaseModel):
    type: Literal["number", "string"]


class FunctionDef(BaseModel):
    name: str
    description: str
    parameters: dict[str, ObjType]
    returns: ObjType


adapter = TypeAdapter(list[FunctionDef])
validated_list = adapter.validate_json(js)
print(validated_list)
