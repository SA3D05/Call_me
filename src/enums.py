from enum import Enum, auto


class State(Enum):
    END = auto()
    NAME = auto()
    START = auto()
    COLON = auto()
    COMMA = auto()
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
