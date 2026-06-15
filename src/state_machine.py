from pprint import pprint

import numpy

from .model import Model
from .enums import State, BraceState, QuotationState
from llm_sdk import Small_LLM_Model


class StateMachine:

    def __init__(self, model: Small_LLM_Model, functions_json: list[dict]):
        self.current_state: State = State.FUN_NAME
        self.functions_json: list[dict] = functions_json
        self.prompt_idx = 0
        self.func_next_id_idx = 0
        self.old_chosen_ids = []
        self.model = model
        self.func_ids = self.__get_func_ids()

    def check_func_ids(self):
        for ids in self.func_ids.values():
            if self.old_chosen_ids == ids:
                return True
        return False

    def get_state(self) -> State:
        return self.current_state

    def __check_can_chose(self, func: str) -> bool:
        func_ids = self.func_ids[func]
        if len(func_ids) <= self.func_next_id_idx:
            return False
        for i, func_id in enumerate(self.old_chosen_ids):
            if func_ids[i] != func_id:
                return False
        return True

    def get_allowed_ids(self) -> tuple[list, list]:
        posible_functions = []
        allowed_ids = set()
        for func, ids in self.func_ids.items():
            if not self.__check_can_chose(func):
                continue
            posible_functions.append(func)
            allowed_ids.add(ids[self.func_next_id_idx])

        allowed_ids = list(allowed_ids)
        return (posible_functions, allowed_ids)

    def update_state(self, chosen_id: int):
        self.func_next_id_idx += 1
        self.old_chosen_ids.append(chosen_id)

    def get_correct_id(self, logits: list[float], allowed_ids: list) -> int:
        empty_vector = numpy.full(len(logits), -numpy.inf)

        np_logits = numpy.array(logits)

        empty_vector[allowed_ids] = np_logits[allowed_ids]

        new_logits = empty_vector.tolist()

        chosen_id: int = numpy.argmax(new_logits)  # type: ignore for numpy shit

        return chosen_id

    def __get_func_ids(self) -> dict[str, list]:
        result: dict[str, list] = {}
        for func in self.functions_json:
            func_name = func["name"]
            func_ids = self.model.encode(func_name).tolist()[0]
            result.setdefault(func_name, []).extend(func_ids)
        return result
