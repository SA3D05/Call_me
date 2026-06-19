import numpy

from llm_sdk import Small_LLM_Model

model = Small_LLM_Model()

prompt = (
    "You are a function parameters extractor agent,"
    + " your goal is to extract the arguments for the function: "
    + "fn_substitute_string_with_regex"
    + " from the user query."
    + "\nseperate the aruments by newline"
    + "\n\nfunction:\n"
    + 'fn_substitute_string_with_regex(source_string: string, regex: string, replacement: string), description: "Replace all occurrences matching a regex pattern in a string."'
    + f"\n\nuser query:\n'Replace all numbers in \"Hello 34 I'm 233 years old\" with NUMBERS'"
    + "\n\nanswer:\n"
    + '"source_string":"'
)
try:
    print(prompt, end="", flush=True)

    ids = model.encode(prompt).tolist()[0]
    for _ in range(20):
        logits = model.get_logits_from_input_ids(ids)
        max_id = numpy.argmax(logits)
        ids.append(max_id)
        print(model.decode([max_id]), end="", flush=True)  # type: ignore
except BaseException:
    pass
