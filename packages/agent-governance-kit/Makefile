.PHONY: demo test typecheck all

demo:
	python examples/demo.py

test:
	python -m pytest --cov=agent_governance_kit --cov-report=term -q

typecheck:
	python -m mypy src/agent_governance_kit

all: test typecheck demo
