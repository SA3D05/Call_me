from .model import Model
from .enums import State, BraceState, QuotationState
from llm_sdk import Small_LLM_Model


class StateMachine:

    def __init__(self, model: Model, functions_json: list[dict], prompts_len: int):
        self.current_state: State = State.START
        self.functions_json: list[dict] = functions_json
        self.prompts_len = prompts_len
        self.prompt_idx = 0
        self.model = model
        self.quotation_state: QuotationState | None = None
        self.brace_state: BraceState | None = None
        self.param_idx: int | None = None
        self.current_function: str | None = None

    def get_correct_id(self, logits: list[float]):
        return self.__get_allowed_ids()

    def __get_params_len(self) -> int:
        for func in self.functions_json:
            if func["name"] == self.current_function:
                return len(func["parameters"])
        return 0

    def update_state(self) -> State:
        match self.current_state:
            case State.START:
                return State.LEFT_BRACE
            case State.LEFT_BRACKET:
                return State.LEFT_BRACE

            case State.LEFT_BRACE:
                if self.brace_state is None or self.brace_state == BraceState.PROMPT:
                    self.quotation_state = QuotationState.PROMPT_NAME_START
                else:
                    self.quotation_state = QuotationState.PARAM_ARG_START
                return State.QUOTATION_MARK

            case State.QUOTATION_MARK:
                match self.quotation_state:
                    case None:
                        self.quotation_state = QuotationState.PROMPT_NAME_END
                    case QuotationState.PROMPT_NAME_START:
                        self.quotation_state = QuotationState.PROMPT_NAME_END
                    case QuotationState.PROMPT_NAME_END:
                        self.quotation_state = QuotationState.PROMPT_START
                    case QuotationState.PROMPT_START:
                        self.quotation_state = QuotationState.PROMPT_END
                    case QuotationState.PROMPT_END:
                        self.quotation_state = QuotationState.NAME_START
                    case QuotationState.NAME_START:
                        self.quotation_state = QuotationState.NAME_END
                    case QuotationState.NAME_END:
                        self.quotation_state = QuotationState.FN_START
                    case QuotationState.FN_START:
                        self.quotation_state = QuotationState.FN_END
                    case QuotationState.FN_END:
                        self.quotation_state = QuotationState.PARAM_START
                    case QuotationState.PARAM_START:
                        self.quotation_state = QuotationState.PARAM_END
                    case QuotationState.PARAM_END:
                        self.quotation_state = QuotationState.PARAM_ARG_START
                    case QuotationState.PARAM_ARG_START:
                        self.quotation_state = QuotationState.PARAM_ARG_END
                    case QuotationState.PARAM_ARG_END:
                        # if argemen value must be string handel it later
                        if self.param_idx < self.__get_params_len():
                            self.param_idx += 1
                            self.quotation_state = QuotationState.PARAM_ARG_START
                        else:
                            self.param_idx = 0
                            self.quotation_state = QuotationState.PROMPT_NAME_START
