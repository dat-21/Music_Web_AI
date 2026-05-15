.PHONY: dev-up test lint docker-build docker-run docker-push ci

dev-up:
	docker-compose up --build

test:
	poetry run pytest tests/ -v
	poetry run pytest --cov=src --cov-report=term-missing tests/

lint:
	poetry run ruff check src tests

docker-build:
	docker build -t ai-search:latest .

docker-run:
	docker run --rm -p 8000:8000 --env-file .env ai-search:latest

docker-push:
	docker push ai-search:latest

ci:
	poetry run ruff check src tests && poetry run pytest --cov=src --cov-report=term-missing tests/ && poetry run bandit -r src -q