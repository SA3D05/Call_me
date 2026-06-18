from src.enums import State


class Writer:

    def __init__(self, prompts: list[str], functions: list[dict]) -> None:

        self.prompts = prompts
        self.functions = functions

        self.indent_level: int = 4
        self.prompt_idx: int = 0
        self.param_idx: int = 0

    def __indent(self, value: int = 0):
        return "\n" + (" " * self.indent_level * value)

    def __write_prompt(self):
        print(
            self.__indent(2),
            '"prompt":"',
            self.prompts[self.prompt_idx],
            '",',
            sep="",
            end="",
            flush=True,
        )

    def __write_name(self):
        print(
            self.__indent(2),
            '"name":"',
            sep="",
            end="",
            flush=True,
        )

    def __write_start(self):
        print(
            "[",
            self.__indent(1),
            "{",
            sep="",
            end="",
            flush=True,
        )

    def __write_midd(self):
        print(
            self.__indent(2),
            "}",
            self.__indent(1),
            "},",
            sep="",
            end="",
            flush=True,
        )

    def __write_parameters(self, arg: str):
        if self.param_idx == 0:

            print(
                '",',
                self.__indent(2),
                '"parameters":{',
                self.__indent(3),
                '"',
                arg,
                '"',
                ":",
                end="",
                sep="",
                flush=True,
            )

        else:
            print(
                '",',
                self.__indent(3),
                '"',
                arg,
                '"',
                ":",
                end="",
                sep="",
                flush=True,
            )

        self.param_idx += 1

    def __write_end(self):
        print(
            ",",
            self.__indent(1),
            "}",
            self.__indent(),
            "]",
        )

    def move_next_prompt(self):
        self.param_idx = 0
        self.prompt_idx += 1

    def write_json(self, state: State, arg: str = ""):

        if state == State.START:
            self.__write_start()
            self.__write_prompt()
            self.__write_name()

        elif state == State.FUN_NAME:
            self.__write_midd()
            self.__write_prompt()
            self.__write_name()

        elif state == State.PARAMETERS:
            self.__write_parameters(arg)

        elif state == State.END:
            self.__write_end()
