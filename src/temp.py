from llm_sdk import Small_LLM_Model

available_functions_json = [
    {
        "name": "fn_add_numbers",
        "description": "Add two numbers together and return their sum.",
        "parameters": {"a": {"type": "number"}, "b": {"type": "number"}},
        "returns": {"type": "number"},
    },
    {
        "name": "fn_greet",
        "description": "Generate a greeting message for a person by name.",
        "parameters": {"name": {"type": "string"}},
        "returns": {"type": "string"},
    },
    {
        "name": "fn_reverse_string",
        "description": "Reverse a string and return the reversed result.",
        "parameters": {"s": {"type": "string"}},
        "returns": {"type": "string"},
    },
    {
        "name": "fn_get_square_root",
        "description": "Calculate the square root of a number.",
        "parameters": {"a": {"type": "number"}},
        "returns": {"type": "number"},
    },
    {
        "name": "fn_substitute_string_with_regex",
        "description": "Replace all occurrences matching a regex pattern in a string.",
        "parameters": {
            "source_string": {"type": "string"},
            "regex": {"type": "string"},
            "replacement": {"type": "string"},
        },
        "returns": {"type": "string"},
    },
]


user_prompts = [
    "What is the sum of 2 and 3?",
    "What is the sum of 12300213 and 1?",
    "Greet shrek",
    "Greet john",
    "Reverse the string 'hello'",
    "Reverse the string 'world'",
    "What is the square root of 16?",
    "Calculate the square root of 144",
    'Replace all numbers in "Hello 34 I\'m 233 years old" with NUMBERS',
    "Replace all vowels in 'Programming is fun' with asterisks",
    "Substitute the word 'cat' with 'dog' in 'The cat sat on the mat with another cat'",
]


model = Small_LLM_Model()

prompt_idx = 0
output = f"""[
{{
        "prompt": {user_prompts[prompt_idx]},
        "name": \""""

functions_names = [
    i
    for i in [
        "fn_add_numbers",
        "fn_greet",
        "fn_reverse_string",
        "fn_get_square_root",
        "fn_substitute_string_with_regex",
    ]
]
functions_names_ids = []

for i in functions_names:
    functions_names_ids.extend(model.encode(i).tolist()[0])


def get_fn_name_prompt(user_query):
    return f"""You are an advanced API routing agent. Your job is to select the correct function from the list of available functions based strictly on the user query.
Available Functions:
{functions_names}

User Query:
"{user_query}"

Output your selection strictly using this layout without conversational intro, markdown codeblocks, or extra text:
Selected Function:
"""


def get_correct_id(logits):
    max_token_id = logits.index(max(logits))
    if functions_names_ids is None:
        return max_token_id
    while max_token_id not in functions_names_ids:

        logits[max_token_id] = float("-inf")
        max_token_id = logits.index(max(logits))

    return max_token_id


def get_input_ids():
    return


print(output, end="")


def generate_fn_name(prompt):
    result = ""
    input_ids = model.encode(get_fn_name_prompt(prompt)).tolist()[0]
    while result not in functions_names:
        # convert the prompt into tokens ids

        # get logits based on the prompt
        logits = model.get_logits_from_input_ids(input_ids)

        # get max id score
        next_token_id = logits.index(max(logits))
        # if the max id score not what i wan't make it -infinity and try the next top score
        while next_token_id not in functions_names_ids:
            logits[next_token_id] = float("-inf")
            next_token_id = logits.index(max(logits))

        input_ids.append(next_token_id)
        current_token = model.decode([next_token_id])
        result += current_token
        print(current_token, end="")
    return result


current_function_name = generate_fn_name(user_prompts[prompt_idx])

# current_function_name = "fn_add_numbers"
current_function_info = {}

for i in available_functions_json:
    if i["name"] == current_function_name:
        current_function_info = i


current_function_parameters = {
    k: v["type"] for k, v in current_function_info["parameters"].items()
}


print(
    f"""\",
        \"parameters\": """,
    end="",
)


def generate_fn_params_prompt(function_info, function_parameters, user_prompt):

    return f"""You are a data extraction agent. Your task is to extract values from the user query matching the required parameters.

Function: {function_info['name']} ({function_info['description']})
Expected Parameters: {function_parameters}

User Query: "{user_prompt}"

Instructions: Extract the values for the requested parameters in the exact order they are listed above. The output shult follow this pattern {function_parameters}. Do not write JSON syntax, do not write the parameter names, do not add spaces around the pipe, and do not include any conversational text.
Extracted Values:
"""


def generate_fn_params(prompt):
    input_ids = model.encode(prompt).tolist()[0]
    result = ""
    while True:
        # convert the prompt into tokens ids

        # get logits based on the prompt
        logits = model.get_logits_from_input_ids(input_ids)

        # get max id score
        next_token_id = logits.index(max(logits))
        # if the max id score not what i wan't make it -infinity and try the next top score
        current_token = model.decode([next_token_id])

        # while not current_token.isdigit() and current_token not in [",","|",".","\n"]:
        #     logits[next_token_id] = float("-inf")
        #     next_token_id = logits.index(max(logits))
        #     current_token = model.decode([next_token_id])

        input_ids.append(next_token_id)
        result += current_token
        print(current_token, end="")


pro = generate_fn_params_prompt(
    current_function_info,
    current_function_parameters,
    user_prompts[prompt_idx],
)


print("\n\nTEST:", pro)
print("result from generating parameters:", generate_fn_params(pro))
# [
#   {
#       "prompt": "What is the sum of 2 and 3?",
#       "name": "fn_add_numbers",
#       "parameters": {"a": 2.0, "b": 3.0}
#   },
#   {
#       "prompt": "Reverse the string 'hello'",
#       "name": "fn_reverse_string",
#       "parameters": {"s": "hello"}
#   },
# ]
