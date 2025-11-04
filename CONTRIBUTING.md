# Contributing to Eloquent Transformers

Thank you for your interest in contributing! This document provides guidelines and instructions.

## Development Setup

1. **Install dependencies**:
   ```bash
   ./scripts/setup.sh
   ```

2. **Start services**:
   ```bash
   docker-compose up -d
   ```

3. **Run migrations**:
   ```bash
   poetry run alembic upgrade head
   ```

4. **Start development server**:
   ```bash
   poetry run uvicorn src.presentation.api.main:app --reload
   ```

## Code Style

We use strict code quality tools:

- **Black**: Code formatting (100 char line length)
- **Ruff**: Fast Python linting
- **mypy**: Static type checking (strict mode)
- **pre-commit**: Automatic checks before commit

### Run code quality checks:

```bash
# Format code
poetry run black src/ tests/

# Lint
poetry run ruff check src/ tests/

# Type check
poetry run mypy src/

# Run all checks
poetry run pre-commit run --all-files
```

## Testing

We maintain high test coverage:

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src --cov-report=html

# Run specific test file
poetry run pytest tests/unit/test_domain_entities.py

# Run specific test
poetry run pytest tests/unit/test_domain_entities.py::TestAudioEntity::test_create_audio
```

### Test Organization:

- `tests/unit/`: Unit tests (domain logic, value objects)
- `tests/integration/`: Integration tests (repositories, services)
- `tests/e2e/`: End-to-end tests (full API flows)

## Architecture Guidelines

### Layer Rules:

1. **Domain Layer**: No external dependencies
   - Pure business logic
   - Rich domain models
   - Domain events

2. **Application Layer**: Orchestration only
   - CQRS commands and queries
   - DTOs for data transfer
   - No business logic

3. **Infrastructure Layer**: External concerns
   - Database access
   - ML models
   - External APIs

4. **Presentation Layer**: User interface
   - API routes
   - Request validation
   - Response formatting

### Dependency Flow:

```
Presentation → Application → Domain
         ↓           ↓
    Infrastructure
```

## Commit Messages

Follow conventional commits:

```
feat: Add audio search endpoint
fix: Correct transcription confidence calculation
docs: Update architecture documentation
test: Add tests for AudioEntity
refactor: Simplify embedding service
```

## Pull Request Process

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the guidelines

3. Ensure all tests pass:
   ```bash
   poetry run pytest
   poetry run pre-commit run --all-files
   ```

4. Commit your changes:
   ```bash
   git add .
   git commit -m "feat: your feature description"
   ```

5. Push and create PR:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Fill out the PR template

## Adding New Features

### Example: Adding a new entity

1. Create domain entity in `src/domain/entities/`
2. Add value objects if needed in `src/domain/value_objects/`
3. Define repository interface in `src/domain/repositories/`
4. Implement repository in `src/infrastructure/persistence/`
5. Create commands/queries in `src/application/`
6. Add API routes in `src/presentation/api/v1/`
7. Write tests for all layers

### Example: Adding a new ML model

1. Create service in `src/infrastructure/ml/`
2. Define interface in `src/domain/services/` if needed
3. Add configuration in `src/infrastructure/config.py`
4. Wire up in `src/presentation/api/dependencies.py`
5. Add tests

## Documentation

- Update README.md for user-facing changes
- Update ARCHITECTURE.md for architectural changes
- Add docstrings to all public functions
- Include examples in docstrings

## Questions?

Open an issue for:
- Bug reports
- Feature requests
- Architecture discussions
- Documentation improvements

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
