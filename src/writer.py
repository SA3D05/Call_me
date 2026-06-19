class Writer:

    def __init__(self, prompts: list[str], functions: list[dict]) -> None:

        self.prompts = prompts
        self.functions = functions
        self.function_context: str = ""
        self.indent_level: int = 4
        self.prompt_idx: int = 0
        self.param_idx: int = 0
        self.result: str = ""

    def __write(self, text: str):
        self.result += text
        print(text, end="", flush=True)

    def __indent(self, value: int = 0):
        return "\n" + (" " * self.indent_level * value)

    def __write_prompt(self, prompt: str):
        text: str = self.__indent(2) + '"prompt":"' + prompt + '",'
        self.__write(text)

    def __write_name_start(self):
        text: str = self.__indent(2) + '"name":"'
        self.__write(text)

    def __write_name_end(self):
        text: str = '",'
        self.__write(text)

    def __write_json_start(self):
        text: str = "["
        self.__write(text)

    def __write_json_end(self):
        text: str = "]"
        self.__write(text)

    def __write_obj_start(self):
        text: str = self.__indent(1) + "{"
        self.__write(text)

    def __write_obj_end(self, is_end: bool = False):
        text: str = self.__indent(1) + "}"

        if not is_end:
            text += ","

        self.__write(text)

    def __write_midd(self):
        text: str = self.__indent(2) + "}" + self.__indent(1) + "},"
        self.__write(text)

    def __write_arg_start(self, arg: str, is_string: bool = False):
        text: str = self.__indent(3) + '"' + arg + '"' + ":" + " "

        if is_string:
            text += '"'

        self.__write(text)

    def __write_arg_end(self, arg, is_string: bool = False, is_last: bool = False):
        text: str = ""

        if is_string:
            text += '"'
        if not is_last:
            text += ","

        self.__write(text)

    def __write_parameters(self):
        text: str = self.__indent(2) + '"parameters":{'
        self.__write(text)

    def __write_end(self):
        text: str = '",' + self.__indent(1) + "}" + self.__indent() + "]" + "\n"
        self.__write(text)

    def move_next_prompt(self):
        self.param_idx = 0
        self.prompt_idx += 1

    def write_start(self, prompt: str):

        self.__write_json_start()
        self.__write_obj_start()

        self.__write_prompt(prompt)
        self.__write_name_start()

    # def write_parameter(self, arg_name: str):
    #     self.__write_name_end()
    #     self.__write_parameters()
    #     self.__write_arg_start()
