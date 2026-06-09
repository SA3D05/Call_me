
FUNC_DEF = data/input/functions_definition.json
INPUT = data/input/function_calling_tests.json
OUTPUT = data/output/function_calls.json


ARGS = --functions_definition --input $(INPUT) $(FUNC_DEF)  --output $(OUTPUT)


run:
	@ uv run --with accelerate python -m src $(ARGS)