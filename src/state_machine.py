from pprint import pprint
import sys

import numpy

from .model import Model
from .enums import ArgType, State
from llm_sdk import Small_LLM_Model


class StateMachine:

    def __init__(self, model: Small_LLM_Model, functions_json: list[dict]):
        self.functions_json: list[dict] = functions_json
        self.prompt_idx: int = 0
        self.current_func: str | None = None
        self.func_next_id_idx: int = 0
        self.old_chosen_func_ids: list[int] = []
        self.old_chosen_args: list[str] = []

        self.model = model
        self.func_ids = self.__get_func_ids()
        self.params_end: bool = False

    def check_func_ids(self):
        for func, ids in self.func_ids.items():
            if self.old_chosen_func_ids == ids:
                self.current_func = func
                return True

        return False

    def __check_can_chose(self, func: str) -> bool:
        func_ids = self.func_ids[func]
        if len(func_ids) <= self.func_next_id_idx:
            return False
        for i, func_id in enumerate(self.old_chosen_func_ids):
            if func_ids[i] != func_id:
                return False
        return True

    def get_allowed_func_ids(self) -> tuple[list, list]:
        posible_functions = []
        allowed_ids = set()
        for func, ids in self.func_ids.items():
            if not self.__check_can_chose(func):
                continue
            posible_functions.append(func)
            allowed_ids.add(ids[self.func_next_id_idx])

        allowed_ids = list(allowed_ids)
        return (posible_functions, allowed_ids)

    def write_correct_arg_id(
        self, logits: list[float], arg_type: ArgType, arg_start: bool = False
    ) -> int:

        max_id: int = numpy.argmax(logits)  # type: ignore
        id_decoded = self.model.decode([max_id])
        if arg_type == ArgType.NUMBER:

            if id_decoded.isdigit() or id_decoded == ".":
                self.old_chosen_args.append(id_decoded)
                print(id_decoded, end="")

            elif '"' in id_decoded:
                if "." not in self.old_chosen_args:
                    print(".0", end="")
                self.old_chosen_args = []
                self.params_end = True

        else:
            # allow only ids that exist in the prompt
            if arg_start:
                print('"', end="")
            if '"' in id_decoded:
                self.old_chosen_args = []
                self.params_end = True
            else:
                print(id_decoded, end="")

        return max_id

    def update_state(self, chosen_id: int):
        self.func_next_id_idx += 1
        self.old_chosen_func_ids.append(chosen_id)

    def get_correct_func_id(self, logits: list[float], allowed_ids: list) -> int:
        empty_vector = numpy.full(len(logits), -numpy.inf)

        np_logits = numpy.array(logits)

        empty_vector[allowed_ids] = np_logits[allowed_ids]

        new_logits = empty_vector.tolist()

        chosen_id: int = numpy.argmax(new_logits)  # type: ignore for numpy shit

        return chosen_id

    def __get_func_ids(self) -> dict[str, list[int]]:
        result: dict[str, list] = {}
        for func in self.functions_json:
            func_name = func["name"]
            func_ids = self.model.encode(func_name).tolist()[0]
            result.setdefault(func_name, []).extend(func_ids)
        return result
