from enum import Enum, auto


class State(Enum):
    START = auto()
    FUN_NAME = auto()
    ARGUMENT = auto()
    PARAMETERS = auto()


class ArgType(Enum):
    STRING = auto()
    NUMBER = auto()
