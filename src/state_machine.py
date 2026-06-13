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
        self.func_idx = 0

        self.model = model
        self.func_ids = self.__get_func_ids()

    def get_state(self) -> State:
        return self.current_state

    def get_correct_logits(self, logits: list[float]) -> list[float]:
        allowed_ids = set()
        can_chose: list[str] = []
        empty_vector = numpy.full(len(logits), -numpy.inf)

        if self.current_state == State.FUN_NAME:
            for func, ids in self.func_ids.items():
                if len(ids) <= self.func_idx:
                    continue
                allowed_ids.add(ids[self.func_idx])
                can_chose.append(func)

        allowed_ids = list(allowed_ids)
        lo = numpy.array(logits)
        empty_vector[allowed_ids] = lo[allowed_ids]
        new_logits = empty_vector.tolist()
        print(self.model.decode([new_logits.index(max(new_logits))]))

        return allowed_ids

    def __get_func_ids(self) -> dict[str, list]:
        result: dict[str, list] = {}
        for func in self.functions_json:
            func_name = func["name"]
            func_ids = self.model.encode(func_name).tolist()[0]
            result.setdefault(func_name, []).extend(func_ids)
        return result
