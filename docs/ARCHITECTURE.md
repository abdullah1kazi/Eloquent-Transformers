# Architecture Documentation

## Overview

Eloquent Transformers is built using **Clean Architecture** principles combined with **Domain-Driven Design (DDD)** and **CQRS** patterns. This architecture ensures:

- **Maintainability**: Clear separation of concerns
- **Testability**: Independent layers with dependency injection
- **Scalability**: Loose coupling enables horizontal scaling
- **Flexibility**: Easy to swap implementations (databases, ML models, etc.)

## Architecture Layers

### 1. Domain Layer (Core Business Logic)

The innermost layer containing pure business logic with **zero external dependencies**.

```
src/domain/
├── entities/          # Rich domain entities with behavior
├── value_objects/     # Immutable value objects
├── events/            # Domain events for side effects
├── repositories/      # Repository interfaces (ports)
├── services/          # Domain services
└── exceptions/        # Domain-specific exceptions
```

#### Key Concepts:

**Entities** (`entities/audio.py`):
- Have identity (ID) that persists over time
- Contain business logic and invariants
- Emit domain events when state changes
- Example: `Audio` aggregate root

**Value Objects** (`value_objects/`):
- Immutable data structures
- Equality based on values, not identity
- Type-safe wrappers (e.g., `AudioId`, `AudioMetadata`)
- Self-validating with business rules

**Domain Events** (`events/`):
- Represent something that happened in the domain
- Enable decoupled communication
- Used for event-driven architecture
- Examples: `AudioUploaded`, `AudioTranscribed`

**Repository Interfaces** (`repositories/`):
- Abstractions for data access (Dependency Inversion)
- Define what operations are needed, not how
- Enable testing with mocks

### 2. Application Layer (Use Cases)

Orchestrates domain objects to fulfill use cases using the **CQRS pattern**.

```
src/application/
├── commands/    # Write operations (change state)
├── queries/     # Read operations (retrieve data)
├── dtos/        # Data Transfer Objects
└── services/    # Application services
```

#### CQRS Pattern:

**Commands** (`commands/`):
- Modify system state
- Return minimal data (usually ID or status)
- Examples: `UploadAudioCommand`, `TranscribeAudioCommand`
- Handler pattern: Each command has a dedicated handler

**Queries** (`queries/`):
- Read-only operations
- Optimized for specific views
- Examples: `GetAudioQuery`, `SearchAudioQuery`
- Can bypass domain layer for performance

**DTOs** (`dtos/`):
- Cross boundary data structures
- Decouple internal models from external APIs
- Prevent leaking domain complexity

**Benefits**:
- Separate read and write concerns
- Optimize each independently
- Scale reads and writes differently
- Clear intent in code

### 3. Infrastructure Layer (External Concerns)

Implements interfaces defined in domain layer.

```
src/infrastructure/
├── persistence/    # Database implementations
├── ml/            # ML model implementations
├── cache/         # Caching implementations
├── messaging/     # Message queue implementations
└── external/      # External API clients
```

#### Key Components:

**Persistence** (`persistence/`):
- SQLAlchemy models and repositories
- Data mapper pattern
- Async database operations
- Migration management

**ML Services** (`ml/`):
- Whisper transcription
- Sentence transformers for embeddings
- Circuit breaker for fault tolerance
- Async wrappers for CPU-bound operations

**Caching** (`cache/`):
- Redis cache implementation
- Cache-aside pattern
- TTL management

### 4. Presentation Layer (API)

User-facing interfaces.

```
src/presentation/
└── api/
    ├── v1/            # API version 1 routes
    ├── middleware/    # Cross-cutting concerns
    ├── dependencies/  # Dependency injection
    └── schemas.py     # Request/response models
```

#### FastAPI Features:

- **Automatic OpenAPI documentation**
- **Request validation** with Pydantic
- **Dependency injection** for handlers
- **Async/await** for high concurrency
- **Middleware** for logging, correlation IDs, etc.

## Design Patterns Used

### 1. Repository Pattern

Abstracts data access, allowing easy swapping of storage implementations.

```python
# Domain layer (interface)
class IAudioRepository(ABC):
    async def save(self, audio: Audio) -> None: ...
    async def find_by_id(self, audio_id: AudioId) -> Optional[Audio]: ...

# Infrastructure layer (implementation)
class AudioRepositoryImpl(IAudioRepository):
    def __init__(self, session: AsyncSession):
        self._session = session
```

### 2. Command Pattern (CQRS)

Encapsulates operations as objects.

```python
@dataclass
class TranscribeAudioCommand:
    audio_id: str

class TranscribeAudioCommandHandler:
    async def handle(self, command: TranscribeAudioCommand) -> TranscriptionDTO:
        # Load aggregate
        # Execute domain logic
        # Persist changes
        # Return result
```

### 3. Factory Pattern

Encapsulates object creation logic.

```python
class Audio:
    @classmethod
    def create(cls, user_id: UserId, ...) -> "Audio":
        audio = cls(...)
        audio._add_event(AudioUploaded(...))
        return audio
```

### 4. Circuit Breaker Pattern

Prevents cascading failures.

```python
@circuit(failure_threshold=5, recovery_timeout=60)
async def transcribe(self, audio_path: str):
    # Protected operation
```

### 5. Dependency Injection

Inverts dependencies for flexibility and testability.

```python
# FastAPI dependencies
def get_upload_handler(
    repository: IAudioRepository = Depends(get_audio_repository),
    processor: IAudioProcessor = Depends(get_audio_processor),
) -> UploadAudioCommandHandler:
    return UploadAudioCommandHandler(repository, processor, storage_path)
```

## Data Flow

### Upload and Transcribe Flow:

```
1. Client → POST /api/v1/audio/upload
2. API Layer validates request
3. UploadAudioCommandHandler creates Audio entity
4. Domain events emitted (AudioUploaded)
5. Repository persists to database
6. Response returned to client

7. Client → POST /api/v1/audio/{id}/transcribe
8. TranscribeAudioCommandHandler loads Audio
9. Domain service (Whisper) transcribes audio
10. Audio.add_transcription() updates state
11. Domain events emitted (AudioTranscribed)
12. Embeddings generated
13. Repository persists changes
14. Response returned
```

### Semantic Search Flow:

```
1. Client → POST /api/v1/audio/search
2. SearchAudioQueryHandler processes query
3. Generate query embeddings
4. Repository performs vector similarity search
5. Results mapped to DTOs
6. Response returned
```

## Event-Driven Architecture

Domain events enable loose coupling:

```
AudioUploaded → Trigger transcription job (Celery)
AudioTranscribed → Generate embeddings
EmbeddingsGenerated → Update search index
```

### Event Bus (Future Enhancement):

```python
# Domain event publisher
class EventBus:
    async def publish(self, event: DomainEvent):
        # Publish to message queue (RabbitMQ/Kafka)
        # Subscribers process asynchronously
```

## Dependency Rules

**The Dependency Rule**: Dependencies point inward. Inner layers know nothing about outer layers.

```
Presentation → Application → Domain
         ↓           ↓
    Infrastructure
```

- **Domain** has NO dependencies
- **Application** depends only on Domain
- **Infrastructure** depends on Domain (implements interfaces)
- **Presentation** depends on Application and Infrastructure

## Testing Strategy

### Unit Tests

Test domain logic in isolation:

```python
def test_add_transcription_changes_status():
    audio = Audio.create(...)
    audio.add_transcription(...)
    assert audio.status == AudioStatus.TRANSCRIBED
```

### Integration Tests

Test with real infrastructure:

```python
async def test_audio_repository_save():
    repo = AudioRepositoryImpl(session)
    audio = Audio.create(...)
    await repo.save(audio)
    loaded = await repo.find_by_id(audio.id)
    assert loaded is not None
```

### E2E Tests

Test through API:

```python
async def test_upload_and_transcribe_flow():
    response = await client.post("/api/v1/audio/upload", files=...)
    audio_id = response.json()["id"]
    response = await client.post(f"/api/v1/audio/{audio_id}/transcribe")
    assert response.status_code == 200
```

## Scalability Considerations

### Horizontal Scaling

- **Stateless API servers**: Scale with load balancer
- **Background workers**: Scale Celery workers independently
- **Database**: Read replicas for queries
- **Cache**: Redis cluster for high availability

### Performance Optimization

- **Async/await**: Non-blocking I/O throughout
- **Connection pooling**: Database and Redis
- **Caching**: Redis for frequently accessed data
- **Lazy loading**: ML models loaded on demand
- **Batch processing**: Process multiple embeddings together

## Security

- **Input validation**: Pydantic schemas at API boundary
- **SQL injection protection**: Parameterized queries
- **Authentication**: JWT tokens (to be implemented)
- **Authorization**: Domain-level access checks
- **Rate limiting**: Prevent abuse
- **Audit logging**: Track all operations

## Monitoring & Observability

- **Structured logging**: JSON logs with correlation IDs
- **Metrics**: Prometheus metrics
- **Tracing**: Correlation IDs across requests
- **Health checks**: `/health` and `/ready` endpoints
- **Dashboards**: Grafana for visualization

## Future Enhancements

1. **Event Sourcing**: Store events as source of truth
2. **Saga Pattern**: Distributed transactions
3. **GraphQL API**: Alternative to REST
4. **WebSocket Support**: Real-time updates
5. **Multi-tenancy**: Tenant isolation
6. **Feature Flags**: Toggle features without deployment
7. **A/B Testing**: Experiment with different ML models

## Conclusion

This architecture provides:
- ✅ Clear separation of concerns
- ✅ Easy to test and maintain
- ✅ Flexible and extensible
- ✅ Production-ready patterns
- ✅ Scalable design

The complexity is justified for enterprise applications requiring long-term maintainability and ability to evolve over time.
