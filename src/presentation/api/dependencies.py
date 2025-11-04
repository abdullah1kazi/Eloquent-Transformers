"""FastAPI dependency injection."""

from typing import AsyncGenerator

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from ...application.commands.transcribe_audio_command import TranscribeAudioCommandHandler
from ...application.commands.upload_audio_command import UploadAudioCommandHandler
from ...application.queries.audio_queries import (
    GetAudioQueryHandler,
    ListUserAudiosQueryHandler,
    SearchAudioQueryHandler,
)
from ...domain.repositories.audio_repository import IAudioRepository
from ...infrastructure.cache.redis_cache import RedisCache
from ...infrastructure.config import Settings, get_settings
from ...infrastructure.ml.audio_processor_impl import AudioProcessorImpl
from ...infrastructure.ml.embedding_service import EmbeddingService
from ...infrastructure.ml.whisper_transcriber import WhisperTranscriber
from ...infrastructure.persistence.audio_repository_impl import AudioRepositoryImpl


# Database session
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=settings.debug)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        yield session


# Redis client
async def get_redis() -> AsyncGenerator[Redis, None]:
    """Get Redis client."""
    settings = get_settings()
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    try:
        yield redis
    finally:
        await redis.aclose()


# Repository
async def get_audio_repository(
    session: AsyncSession = Depends(get_db_session),
) -> IAudioRepository:
    """Get audio repository."""
    return AudioRepositoryImpl(session)


# ML Services
def get_whisper_transcriber() -> WhisperTranscriber:
    """Get Whisper transcriber."""
    settings = get_settings()
    return WhisperTranscriber(model_name=settings.whisper_model, device=settings.device)


def get_embedding_service() -> EmbeddingService:
    """Get embedding service."""
    settings = get_settings()
    return EmbeddingService(model_name=settings.embedding_model, device=settings.device)


def get_audio_processor(
    transcriber: WhisperTranscriber = Depends(get_whisper_transcriber),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
) -> AudioProcessorImpl:
    """Get audio processor."""
    return AudioProcessorImpl(transcriber, embedding_service)


# Command Handlers
def get_upload_audio_handler(
    repository: IAudioRepository = Depends(get_audio_repository),
    processor: AudioProcessorImpl = Depends(get_audio_processor),
) -> UploadAudioCommandHandler:
    """Get upload audio command handler."""
    settings = get_settings()
    return UploadAudioCommandHandler(repository, processor, settings.storage_path)


def get_transcribe_audio_handler(
    repository: IAudioRepository = Depends(get_audio_repository),
    processor: AudioProcessorImpl = Depends(get_audio_processor),
) -> TranscribeAudioCommandHandler:
    """Get transcribe audio command handler."""
    return TranscribeAudioCommandHandler(repository, processor)


# Query Handlers
def get_audio_query_handler(
    repository: IAudioRepository = Depends(get_audio_repository),
) -> GetAudioQueryHandler:
    """Get audio query handler."""
    return GetAudioQueryHandler(repository)


def get_list_audios_handler(
    repository: IAudioRepository = Depends(get_audio_repository),
) -> ListUserAudiosQueryHandler:
    """Get list audios query handler."""
    return ListUserAudiosQueryHandler(repository)


def get_search_handler(
    repository: IAudioRepository = Depends(get_audio_repository),
    processor: AudioProcessorImpl = Depends(get_audio_processor),
) -> SearchAudioQueryHandler:
    """Get search query handler."""
    return SearchAudioQueryHandler(repository, processor)


# Cache
async def get_cache(redis: Redis = Depends(get_redis)) -> RedisCache:
    """Get cache."""
    settings = get_settings()
    return RedisCache(redis, ttl=settings.redis_ttl)
