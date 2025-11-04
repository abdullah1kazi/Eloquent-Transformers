# Makefile for common development tasks

.PHONY: help install run test lint format clean docker-up docker-down migrate

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	poetry install
	poetry run pre-commit install

run:  ## Start development server
	poetry run uvicorn src.presentation.api.main:app --reload --host 0.0.0.0 --port 8000

test:  ## Run tests with coverage
	poetry run pytest --cov=src --cov-report=html --cov-report=term

test-unit:  ## Run unit tests only
	poetry run pytest tests/unit/ -v

test-integration:  ## Run integration tests only
	poetry run pytest tests/integration/ -v

lint:  ## Run linting checks
	poetry run ruff check src/ tests/
	poetry run mypy src/

format:  ## Format code
	poetry run black src/ tests/
	poetry run ruff check --fix src/ tests/

quality:  ## Run all quality checks
	poetry run black --check src/ tests/
	poetry run ruff check src/ tests/
	poetry run mypy src/
	poetry run pytest --cov=src

docker-up:  ## Start all services with docker-compose
	docker-compose up -d

docker-down:  ## Stop all services
	docker-compose down

docker-logs:  ## View docker logs
	docker-compose logs -f

docker-build:  ## Build docker images
	docker-compose build

migrate:  ## Run database migrations
	poetry run alembic upgrade head

migrate-create:  ## Create new migration (usage: make migrate-create message="your message")
	poetry run alembic revision --autogenerate -m "$(message)"

migrate-down:  ## Rollback last migration
	poetry run alembic downgrade -1

clean:  ## Clean up cache and temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov/ dist/ build/

setup:  ## Initial setup
	./scripts/setup.sh

docs:  ## Open API documentation
	@echo "Opening API documentation..."
	@echo "Swagger UI: http://localhost:8000/docs"
	@echo "ReDoc: http://localhost:8000/redoc"

check:  ## Run all checks before commit
	@echo "Running pre-commit checks..."
	poetry run pre-commit run --all-files
	@echo "Running tests..."
	poetry run pytest
	@echo "✅ All checks passed!"
