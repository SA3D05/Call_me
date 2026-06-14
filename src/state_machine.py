from pprint import pprint

import numpy

from .model import Model
from .enums import State, BraceState, QuotationState
from llm_sdk import Small_LLM_Model


class StateMachine:

    def __init__(
        self, model: Small_LLM_Model, functions_json: list[dict], prompts_len: int
    ):
        self.current_state: State = State.FUN_NAME
        self.functions_json: list[dict] = functions_json
        self.prompts_len = prompts_len
        self.prompt_idx = 0
        self.func_next_id_idx = 0
        self.old_chosen_ids = []
        self.model = model
        self.func_ids = self.__get_func_ids()

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

    def get_posible_next_ids(self) -> tuple[list, list]:
        result = ([], [])
        allowed_ids = set()
        for func, ids in self.func_ids.items():
            if not self.__check_can_chose(func):
                continue
            result[0].append(func)
            allowed_ids.add(ids[self.func_next_id_idx])

        result[1].extend(allowed_ids)
        return result

    def get_correct_id(self, logits: list[float], allowed_ids: list) -> int:
        empty_vector = numpy.full(len(logits), -numpy.inf)

        np_logits = numpy.array(logits)

        empty_vector[allowed_ids] = np_logits[allowed_ids]

        new_logits = empty_vector.tolist()

        chosen_id: int = numpy.argmax(new_logits)  # type: ignore for numpy shit

        self.old_chosen_ids.append(chosen_id)

        self.func_next_id_idx += 1

        return chosen_id

    def __get_func_ids(self) -> dict[str, list]:
        result: dict[str, list] = {}
        for func in self.functions_json:
            func_name = func["name"]
            func_ids = self.model.encode(func_name).tolist()[0]
            result.setdefault(func_name, []).extend(func_ids)
        return result
