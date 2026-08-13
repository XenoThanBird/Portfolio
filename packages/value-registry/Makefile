.PHONY: demo test typecheck catalog all

demo:
	python -m value_registry.cli score --rubric examples/rubric.yaml --portfolio examples/portfolio.yaml --out out/portfolio_report.md
	python -m value_registry.cli generate-catalog --out out/catalog.yaml
	python -m value_registry.cli registry-report --catalog out/catalog.yaml --out out/registry_report.md
	@echo "demo complete: see out/portfolio_report.md and out/registry_report.md"

catalog:
	python -m value_registry.cli generate-catalog --out data/catalog.yaml

test:
	python -m pytest --cov=value_registry --cov-fail-under=80 -q

typecheck:
	python -m mypy src/value_registry

all: test typecheck demo
