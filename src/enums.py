from enum import Enum, auto


class State(Enum):
    END = auto()
    NAME = auto()
    START = auto()
    COLON = auto()
    COMMA = auto()
    RESULT = auto()
    NUMBER = auto()
    STRING = auto()
    PROMPT = auto()
    FUN_NAME = auto()
    PARAMETERS = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    LEFT_BRACKET = auto()
    RIGHT_BRACKET = auto()
    QUOTATION_MARK = auto()


class BraceState(Enum):
    PROMPT = auto()
    PARAMETERS = auto()


class QuotationState(Enum):
    PROMPT_NAME_START = auto()
    PROMPT_NAME_END = auto()

    PROMPT_START = auto()
    PROMPT_END = auto()

    NAME_START = auto()
    NAME_END = auto()

    FN_START = auto()
    FN_END = auto()

    PARAM_START = auto()
    PARAM_END = auto()

    PARAM_ARG_START = auto()
    PARAM_ARG_END = auto()
