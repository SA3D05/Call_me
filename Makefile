
FUNC_DEF = data/input/functions_definition.json
INPUT = data/input/function_calling_tests.json
OUTPUT = data/output/function_calls.json


ARGS = --functions_definition $(FUNC_DEF)  --input   $(INPUT) --output  $(OUTPUT)


run:
	@ uv run --with accelerate python -m src $(ARGS)
# 	@ python3 -m src $(ARGS)

test:
	@ python3 src/test.py