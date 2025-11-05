.PHONY: dev test lint type-check docs clean

dev:
	PYTHONPATH=. streamlit run ui/app.py

test:
	PYTHONPATH=. pytest --cov=src --cov-report=term --cov-report=html

lint:
	ruff check src tests

type-check:
	mypy src

docs:
	@echo "Generating documentation..."
	@python -c "from src.graph.builder import build_graph; from src.core.blueprint_parser import BlueprintParser; import json; bp = BlueprintParser(); wf = bp.parse(json.dumps({'workflow_name': 'test'})); graph = build_graph(wf)"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage
