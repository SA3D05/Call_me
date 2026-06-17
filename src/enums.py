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
    ARGUMENTS_START = auto()
    ARGUMENTS_END = auto()
    ARGUMENTS_NEXT = auto()
    PARAMETERS = auto()


class ArgType(Enum):
    STRING = auto()
    NUMBER = auto()
