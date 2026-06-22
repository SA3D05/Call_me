from llm_sdk import Small_LLM_Model


class Model:
    def __init__(self, prompts: list, functions: list):
        self.model = Small_LLM_Model()
        self.prompts = prompts
        self.functions = functions
        self.func_idx = 0

        self.prompt_idx: int = 0
        self.input_ids: list[int] = []
        self.indent_level = 4
        self.param_idx = 0
        self.params_names = []

    def __set_func_params(self, target_func: str):

        for func in self.functions:
            if func["name"] == target_func:
                for param in func["parameters"].keys():
                    self.params_names.append(param)

    def get_func_info(self, target_func: str = "") -> str:
        result = ""
        for func in self.functions:
            if target_func != "" and func["name"] != target_func:
                continue
            first = True
            result += func["name"] + "("
            for param_name, param_type in func["parameters"].items():
                result += ", " if not first else ""
                result += param_name + ": " + param_type["type"]
                first = False
            result += "), description: " + func["description"] + "\n"
        return result

    def set_func_input_ids(self, current_prompt: str):

        functions_info = self.get_func_info()

        prompt = (
            "You are a function selector agent,"
            + " your goal is to select the correct"
            + " function name based on the user query."
            + "\n\nfunctions:\n"
            + functions_info
            + "\nuser query:\n"
            + f'"{current_prompt}"'
            + "\n\nanswer:\n"
            + "fn_"
        )
        self.input_ids = []
        ids = self.model.encode(prompt).tolist()[0]
        self.input_ids.extend(ids)

    def set_param_input_ids(self, target_func: str, current_prompt: str):

        function_info = self.get_func_info(target_func)
        self.__set_func_params(target_func)

        prompt = (
            "You are a data extraction tool. Do NOT solve math problems. Do NOT answer questions. "
            "Only extract the raw numbers or words from the query that match the function parameters.\n\n"
            f"Extract the arguments for the function '{target_func}' based ONLY on the user query.\n"
            "Format the output strictly as 'argument_name: value'. One per line. Do not write anything else.\n\n"
            "# Example\n"
            "Function: book_flight(destination, passengers)\n"
            "Query: I want to fly to Paris with 2 people.\n"
            "Answer:\n"
            "destination: Paris\n"
            "passengers: 2\n\n"
            "# Task\n"
            f"Function:\n{function_info}\n\n"
            f"Query:\n{current_prompt}\n\n"
            "Answer:\n"
        )
        self.input_ids = []
        ids = self.model.encode(prompt).tolist()[0]
        self.input_ids.extend(ids)

    def update_param_input_ids(self, is_first: bool, next_param_name: str):

        prompt = ""

        if not is_first:
            prompt += '"\n'

        prompt += f'"{next_param_name}":"'

        ids: list[int] = self.model.encode(prompt).tolist()[0]
        self.input_ids.extend(ids)

    def generate_logits(self) -> list[float]:
        logits = self.model.get_logits_from_input_ids(self.input_ids)

        return logits

    def set_token_id(self, token_id: int) -> str:
        self.input_ids.append(token_id)
        return self.model.decode([token_id])
