.PHONY: install test lint run-api

install:
	poetry install

test:
	poetry run pytest tests/

lint:
	poetry run ruff check src/ tests/
	poetry run black --check src/ tests/

format:
	poetry run black src/ tests/
	poetry run ruff check --fix src/ tests/

run-api:
	poetry run uvicorn src.serving.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	cd frontend && npm run dev
