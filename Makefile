.PHONY: install test lint format run-api run-frontend run-ingestion

install:
	python3 -m poetry install

test:
	python3 -m poetry run pytest tests/

lint:
	python3 -m poetry run ruff check src/ tests/
	python3 -m poetry run black --check src/ tests/

format:
	python3 -m poetry run black src/ tests/
	python3 -m poetry run ruff check --fix src/ tests/

run-api:
	python3 -m poetry run uvicorn src.serving.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	cd frontend && npm run dev

run-ingestion:
	python3 -m poetry run python -m src.ingestion.run_ingestion
