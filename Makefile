export UV_CACHE_DIR := /goinfre/satifi/.uv_cache
export HF_HOME      := /goinfre/satifi/.hf_cache



FUNC_DEF = data/input/functions_definition.json
INPUT = data/input/function_calling_tests.json
OUTPUT = data/output/function_calls.json

ARGS = --functions_definition $(FUNC_DEF)  --input   $(INPUT) --output  $(OUTPUT)

run:
	uv run python -m src $(ARGS)

install:
	uv sync

debug:
	python3 -m pdb main.py

clean:
	rm -rf .mypy_cache
	find . -name "__pycache__" -type d -exec rm -rf {} +


lint:
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
	flake8 --extend-exclude=.venv .