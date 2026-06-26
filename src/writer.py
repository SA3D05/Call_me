class Writer:

    def __init__(self, prompts: list[str], functions: list[dict]) -> None:

        self.prompts = prompts
        self.functions = functions

        self.indent_level: int = 4
        self.prompt_idx: int = 0

        self.result: str = ""
        self.parameters_writted: bool = False

        self.params: list[tuple[str, str]] = []
        self.last_arg_type: str | None = None

        self.json_start_writted: bool = False

    def __write(self, text: str) -> None:
        self.result += text
        print(text, end="", flush=True)

    def build_context(self, func: str) -> None:
        for f in self.functions:
            if f["name"] != func:
                continue
            for param_name, param_type in f["parameters"].items():
                self.params.insert(0, (param_name, param_type["type"]))

    def __indent(self, value: int = 0) -> str:
        return "\n" + (" " * self.indent_level * value)

    def __write_prompt(self) -> None:
        text: str = self.__indent(2) + '"prompt":"'

        for c in self.prompts[self.prompt_idx]:
            if c == '"' or c == "\\":
                text += "\\"
            text += c

        text += '",'
        self.__write(text)

    def __write_name_start(self) -> None:
        text: str = self.__indent(2) + '"name":"'
        self.__write(text)

    def __write_name_end(self) -> None:
        text: str = '",'
        self.__write(text)

    def __write_json_start(self) -> None:
        text: str = "["
        self.__write(text)

    def __write_obj_start(self) -> None:
        text: str = self.__indent(1) + "{"
        self.__write(text)

    def __write_obj_end(self) -> None:

        text: str = ""

        if self.last_arg_type == "string":
            text += '"'
        text += self.__indent(2) + "}" + self.__indent(1) + "}"

        if self.prompt_idx < len(self.prompts):
            text += ","

        self.__write(text)

    def __write_arg_start(self, arg: str, param_type: str) -> None:
        text: str = self.__indent(3) + '"' + arg + '"' + ":" + " "

        if param_type == "string":
            text += '"'

        self.__write(text)

    def __write_arg_end(self, is_last: bool = False) -> None:

        text: str = ""
        if self.last_arg_type == "string":
            text += '"'
        if not is_last:
            text += ","

        self.__write(text)

    def __write_parameters_start(self) -> None:
        text: str = self.__indent(2) + '"parameters":{'
        self.__write(text)

    def write_end(self) -> None:
        text: str = ""
        if self.last_arg_type == "string":
            text += '"'
        text += (
            self.__indent(2)
            + "}"
            + self.__indent(1)
            + "}"
            + self.__indent()
            + "]"
            + "\n"
        )
        self.__write(text)

    def write_next_obj(self) -> None:
        self.parameters_writted = False

        if not self.json_start_writted:
            self.__write_json_start()
            self.json_start_writted = True

        if self.prompt_idx != 0:
            self.__write_obj_end()
            self.last_arg_type = None

        self.__write_obj_start()

        self.__write_prompt()
        self.prompt_idx += 1
        self.__write_name_start()

    def write_next_param(self) -> None:
        if not self.parameters_writted:
            self.__write_name_end()
            self.__write_parameters_start()
            self.parameters_writted = True
        if self.last_arg_type:
            self.__write_arg_end()

        param_name, param_type = self.params.pop()
        self.last_arg_type = param_type
        self.__write_arg_start(param_name, param_type)
