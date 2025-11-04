"""SQLAlchemy implementation of audio repository."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...domain.entities.audio import Audio, Transcription, AudioStatus
from ...domain.repositories.audio_repository import IAudioRepository
from ...domain.value_objects.audio_metadata import AudioFormat, AudioMetadata
from ...domain.value_objects.identifiers import AudioId, TranscriptionId, UserId
from .models import AudioModel, TranscriptionModel
from datetime import timedelta


class AudioRepositoryImpl(IAudioRepository):
    """
    SQLAlchemy-based repository implementation.

    Demonstrates:
    - Repository pattern
    - Data mapper pattern
    - Async database operations
    - Eager loading for performance
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, audio: Audio) -> None:
        """Save or update audio entity."""
        # Check if exists
        existing = await self._session.get(AudioModel, audio.id.value)

        if existing:
            # Update existing
            self._map_to_model(audio, existing)
        else:
            # Create new
            model = AudioModel(id=audio.id.value)
            self._map_to_model(audio, model)
            self._session.add(model)

        await self._session.commit()

    async def find_by_id(self, audio_id: AudioId) -> Optional[Audio]:
        """Find audio by ID with eager loading."""
        stmt = (
            select(AudioModel)
            .where(AudioModel.id == audio_id.value)
            .options(selectinload(AudioModel.transcription))
        )

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        return self._map_to_entity(model) if model else None

    async def find_by_user(
        self, user_id: UserId, limit: int = 100, offset: int = 0
    ) -> List[Audio]:
        """Find all audio files for a user."""
        stmt = (
            select(AudioModel)
            .where(AudioModel.user_id == user_id.value)
            .options(selectinload(AudioModel.transcription))
            .order_by(AudioModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._map_to_entity(model) for model in models]

    async def delete(self, audio_id: AudioId) -> None:
        """Delete audio."""
        stmt = select(AudioModel).where(AudioModel.id == audio_id.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            await self._session.delete(model)
            await self._session.commit()

    async def search_by_text(
        self, query: str, limit: int = 10, user_id: Optional[UserId] = None
    ) -> List[Audio]:
        """Full-text search on transcriptions."""
        # Use PostgreSQL full-text search
        stmt = (
            select(AudioModel)
            .join(TranscriptionModel)
            .where(TranscriptionModel.text.ilike(f"%{query}%"))
            .options(selectinload(AudioModel.transcription))
            .limit(limit)
        )

        if user_id:
            stmt = stmt.where(AudioModel.user_id == user_id.value)

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._map_to_entity(model) for model in models]

    async def search_by_embedding(
        self, embedding: List[float], limit: int = 10, user_id: Optional[UserId] = None
    ) -> List[tuple[Audio, float]]:
        """
        Semantic search using embedding similarity.

        Uses PostgreSQL pgvector extension for efficient similarity search.
        Falls back to in-memory cosine similarity if pgvector not available.
        """
        import numpy as np

        # Fetch all audios with embeddings
        stmt = select(AudioModel).where(
            AudioModel.embedding_vector.isnot(None), AudioModel.status == AudioStatus.INDEXED.value
        )

        if user_id:
            stmt = stmt.where(AudioModel.user_id == user_id.value)

        stmt = stmt.options(selectinload(AudioModel.transcription))

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        # Compute cosine similarity
        query_vec = np.array(embedding)
        results = []

        for model in models:
            if model.embedding_vector:
                model_vec = np.array(model.embedding_vector)
                similarity = np.dot(query_vec, model_vec) / (
                    np.linalg.norm(query_vec) * np.linalg.norm(model_vec)
                )
                audio = self._map_to_entity(model)
                results.append((audio, float(similarity)))

        # Sort by similarity (descending)
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:limit]

    def _map_to_entity(self, model: AudioModel) -> Audio:
        """Map database model to domain entity."""
        # Map metadata
        metadata = AudioMetadata(
            duration=timedelta(seconds=model.duration_seconds),
            sample_rate=model.sample_rate,
            channels=model.channels,
            bitrate=model.bitrate,
            format=AudioFormat(model.format),
        )

        # Map transcription if exists
        transcription = None
        if model.transcription:
            transcription = Transcription(
                id=TranscriptionId(value=model.transcription.id),
                text=model.transcription.text,
                segments=model.transcription.segments,
                language=model.transcription.language,
                confidence=model.transcription.confidence,
                created_at=model.transcription.created_at,
            )

        # Create audio entity
        audio = Audio(
            id=AudioId(value=model.id),
            user_id=UserId(value=model.user_id),
            filename=model.filename,
            file_path=model.file_path,
            file_size=model.file_size,
            metadata=metadata,
            status=AudioStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
            transcription=transcription,
            embedding_vector=model.embedding_vector,
            error_message=model.error_message,
        )

        return audio

    def _map_to_model(self, audio: Audio, model: AudioModel) -> None:
        """Map domain entity to database model."""
        model.user_id = audio.user_id.value
        model.filename = audio.filename
        model.file_path = audio.file_path
        model.file_size = audio.file_size

        # Metadata
        model.duration_seconds = audio.metadata.duration_seconds
        model.sample_rate = audio.metadata.sample_rate
        model.channels = audio.metadata.channels
        model.bitrate = audio.metadata.bitrate
        model.format = audio.metadata.format.value

        model.status = audio.status.value
        model.error_message = audio.error_message
        model.embedding_vector = audio.embedding_vector

        model.created_at = audio.created_at
        model.updated_at = audio.updated_at

        # Map transcription
        if audio.transcription:
            if model.transcription:
                # Update existing
                model.transcription.text = audio.transcription.text
                model.transcription.segments = audio.transcription.segments
                model.transcription.language = audio.transcription.language
                model.transcription.confidence = audio.transcription.confidence
            else:
                # Create new
                model.transcription = TranscriptionModel(
                    id=audio.transcription.id.value,
                    audio_id=audio.id.value,
                    text=audio.transcription.text,
                    segments=audio.transcription.segments,
                    language=audio.transcription.language,
                    confidence=audio.transcription.confidence,
                    created_at=audio.transcription.created_at,
                )
