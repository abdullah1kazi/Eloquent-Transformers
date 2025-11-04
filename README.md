# 🎙️ Eloquent Transformers - Enterprise Audio Intelligence Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

An **enterprise-grade audio intelligence platform** leveraging state-of-the-art transformer models for audio transcription, semantic search, and analysis. Built with production-ready architecture patterns and modern Python best practices.

## 🌟 Key Features

### 🏗️ **Enterprise Architecture**
- **Clean Architecture** with clear separation of concerns
- **Domain-Driven Design (DDD)** with rich domain models
- **CQRS Pattern** for scalable command/query separation
- **Event-Driven Architecture** for loosely coupled components
- **Hexagonal Architecture** for testability and flexibility

### 🚀 **Modern Technology Stack**
- **FastAPI** with automatic OpenAPI documentation
- **Async/Await** throughout for high concurrency
- **Type Safety** with strict mypy checking
- **Pydantic V2** for data validation
- **SQLAlchemy 2.0** with async support
- **Redis** for caching and pub/sub
- **Celery** for background task processing
- **PostgreSQL** for reliable data storage

### 🤖 **AI/ML Capabilities**
- **OpenAI Whisper** for state-of-the-art transcription
- **Sentence Transformers** for semantic embeddings
- **ChromaDB** for vector similarity search
- **CLAP Models** for audio-text multimodal understanding
- **Streaming Inference** for real-time processing

### 🔧 **Production-Ready Features**
- **Circuit Breaker Pattern** for fault tolerance
- **Rate Limiting** with token bucket algorithm
- **Distributed Caching** with Redis
- **Health Checks** and readiness probes
- **Structured Logging** with correlation IDs
- **OpenTelemetry** for distributed tracing
- **Prometheus Metrics** for monitoring
- **Graceful Shutdown** handling

### 🔒 **Security & Reliability**
- **JWT Authentication** with refresh tokens
- **Role-Based Access Control (RBAC)**
- **Input Validation** at all layers
- **SQL Injection Protection**
- **Rate Limiting** per user/IP
- **Audit Logging** for compliance

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                       │
│                    (FastAPI REST API)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   Application Layer                          │
│           (Use Cases, Commands, Queries, DTOs)               │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                     Domain Layer                             │
│     (Entities, Value Objects, Domain Events, Services)       │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  Infrastructure Layer                        │
│  (Repositories, External APIs, ML Models, Message Queue)     │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Poetry (Python dependency management)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/eloquent-transformers.git
cd eloquent-transformers
```

2. **Install dependencies**
```bash
poetry install
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Start services with Docker Compose**
```bash
docker-compose up -d
```

5. **Run database migrations**
```bash
poetry run alembic upgrade head
```

6. **Start the application**
```bash
poetry run uvicorn src.presentation.api.main:app --reload
```

Visit `http://localhost:8000/docs` for interactive API documentation.

## 🏗️ Project Structure

```
eloquent-transformers/
├── src/
│   ├── domain/                    # Domain Layer (Business Logic)
│   │   ├── entities/             # Domain entities
│   │   ├── value_objects/        # Immutable value objects
│   │   ├── events/               # Domain events
│   │   ├── repositories/         # Repository interfaces
│   │   └── services/             # Domain services
│   ├── application/              # Application Layer (Use Cases)
│   │   ├── commands/             # Command handlers (CQRS)
│   │   ├── queries/              # Query handlers (CQRS)
│   │   ├── dtos/                 # Data Transfer Objects
│   │   └── services/             # Application services
│   ├── infrastructure/           # Infrastructure Layer
│   │   ├── persistence/          # Database implementations
│   │   ├── ml/                   # ML model implementations
│   │   ├── cache/                # Caching implementations
│   │   ├── messaging/            # Message queue implementations
│   │   └── external/             # External service clients
│   └── presentation/             # Presentation Layer
│       └── api/                  # FastAPI routes and schemas
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── e2e/                      # End-to-end tests
├── docker/                       # Docker configurations
├── docs/                         # Documentation
├── scripts/                      # Utility scripts
└── alembic/                      # Database migrations
```

## 📚 Core Concepts

### Clean Architecture Layers

1. **Domain Layer**: Pure business logic, no external dependencies
   - Entities with rich behavior
   - Value Objects for type safety
   - Domain Events for side effects
   - Repository interfaces

2. **Application Layer**: Orchestrates domain objects
   - Commands for write operations
   - Queries for read operations
   - DTOs for data transfer
   - Use case implementations

3. **Infrastructure Layer**: External concerns
   - Database access
   - ML model inference
   - External APIs
   - Caching and messaging

4. **Presentation Layer**: User interface
   - REST API endpoints
   - Request/response models
   - Authentication/authorization

### CQRS Pattern

Separates read and write operations for optimal performance:
- **Commands**: Modify state, return minimal data
- **Queries**: Read-only, optimized for specific views

### Event-Driven Architecture

Decouples components through domain events:
- Audio uploaded → Transcription triggered
- Transcription completed → Embeddings generated
- Embeddings ready → Search index updated

## 🧪 Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src --cov-report=html

# Run specific test types
poetry run pytest tests/unit
poetry run pytest tests/integration
poetry run pytest tests/e2e

# Run with type checking
poetry run mypy src/
```

## 🔍 Code Quality

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

## 📊 Monitoring & Observability

- **Prometheus Metrics**: `http://localhost:9090`
- **Grafana Dashboards**: `http://localhost:3000`
- **Application Logs**: Structured JSON logs with correlation IDs
- **Distributed Tracing**: OpenTelemetry integration
- **Health Checks**: `/health` and `/ready` endpoints

## 🐳 Docker Deployment

```bash
# Build image
docker build -t eloquent-transformers:latest .

# Run with docker-compose
docker-compose up -d

# Scale workers
docker-compose up -d --scale celery-worker=4

# View logs
docker-compose logs -f
```

## 📖 API Documentation

Interactive API documentation is available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Spec**: `http://localhost:8000/openapi.json`

### Example API Usage

```python
import httpx

# Upload audio file
async with httpx.AsyncClient() as client:
    files = {"file": open("audio.mp3", "rb")}
    response = await client.post(
        "http://localhost:8000/api/v1/audio/upload",
        files=files
    )
    audio_id = response.json()["id"]

    # Get transcription
    response = await client.get(
        f"http://localhost:8000/api/v1/audio/{audio_id}/transcription"
    )
    transcription = response.json()

    # Semantic search
    response = await client.post(
        "http://localhost:8000/api/v1/audio/search",
        json={"query": "machine learning discussion", "limit": 10}
    )
    results = response.json()
```

## 🌟 Advanced Features

### 1. **Semantic Audio Search**
Search audio content by meaning, not just keywords:
```python
# Find audio clips about "artificial intelligence" even if those
# exact words aren't spoken
results = await search_audio_semantic("AI and machine learning")
```

### 2. **Real-time Streaming Transcription**
Process audio as it's being recorded:
```python
async for chunk in stream_transcription(audio_stream):
    print(chunk.text)
```

### 3. **Multi-language Support**
Automatic language detection and transcription in 100+ languages

### 4. **Speaker Diarization**
Identify who spoke when in multi-speaker audio

### 5. **Audio Summarization**
Generate concise summaries of long audio content

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI Whisper for transcription models
- Hugging Face for transformer models
- FastAPI for the excellent web framework
- The open-source community

## 📞 Contact

- **Author**: Your Name
- **Email**: your.email@example.com
- **LinkedIn**: [Your Profile](https://linkedin.com/in/yourprofile)
- **GitHub**: [@yourusername](https://github.com/yourusername)

---

**Built with ❤️ using modern Python and enterprise architecture patterns**
