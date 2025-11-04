"""Queries for audio data."""

from dataclasses import dataclass
from typing import List, Optional

from ..dtos.audio_dtos import AudioDTO, SearchResultDTO, TranscriptionDTO
from ...domain.repositories.audio_repository import IAudioRepository
from ...domain.services.audio_processor import IAudioProcessor
from ...domain.value_objects.identifiers import AudioId, UserId
from ...domain.exceptions import AudioNotFoundException
from ...domain.entities.audio import Audio


class AudioMapper:
    """Maps domain entities to DTOs."""

    @staticmethod
    def to_dto(audio: Audio) -> AudioDTO:
        """Convert Audio entity to DTO."""
        transcription_dto = None
        if audio.transcription:
            transcription_dto = TranscriptionDTO(
                id=str(audio.transcription.id),
                text=audio.transcription.text,
                language=audio.transcription.language,
                confidence=audio.transcription.confidence,
                word_count=len(audio.transcription.text.split()),
                created_at=audio.transcription.created_at,
                segments=audio.transcription.segments,
            )

        return AudioDTO(
            id=str(audio.id),
            user_id=str(audio.user_id),
            filename=audio.filename,
            file_size=audio.file_size,
            duration_seconds=audio.metadata.duration_seconds,
            sample_rate=audio.metadata.sample_rate,
            format=audio.metadata.format.value,
            status=audio.status.value,
            created_at=audio.created_at,
            transcription=transcription_dto,
            has_embeddings=audio.embedding_vector is not None,
        )


@dataclass
class GetAudioQuery:
    """Query to get audio by ID."""

    audio_id: str
    user_id: str


class GetAudioQueryHandler:
    """Handler for get audio query."""

    def __init__(self, audio_repository: IAudioRepository) -> None:
        self._repository = audio_repository

    async def handle(self, query: GetAudioQuery) -> AudioDTO:
        """
        Handle get audio query.

        Demonstrates:
        - Query pattern (read-only)
        - DTO mapping
        - Authorization check
        """
        audio_id = AudioId.from_str(query.audio_id)
        audio = await self._repository.find_by_id(audio_id)

        if not audio:
            raise AudioNotFoundException(query.audio_id)

        # Authorization check
        if str(audio.user_id) != query.user_id:
            from ...domain.exceptions import UnauthorizedException

            raise UnauthorizedException("You don't have access to this audio")

        return AudioMapper.to_dto(audio)


@dataclass
class ListUserAudiosQuery:
    """Query to list user's audio files."""

    user_id: str
    limit: int = 100
    offset: int = 0


class ListUserAudiosQueryHandler:
    """Handler for list user audios query."""

    def __init__(self, audio_repository: IAudioRepository) -> None:
        self._repository = audio_repository

    async def handle(self, query: ListUserAudiosQuery) -> List[AudioDTO]:
        """Handle list user audios query."""
        user_id = UserId.from_str(query.user_id)
        audios = await self._repository.find_by_user(
            user_id=user_id, limit=query.limit, offset=query.offset
        )

        return [AudioMapper.to_dto(audio) for audio in audios]


@dataclass
class SearchAudioQuery:
    """Query to search audio by semantic meaning."""

    query_text: str
    user_id: Optional[str] = None
    limit: int = 10


class SearchAudioQueryHandler:
    """Handler for semantic audio search query."""

    def __init__(
        self,
        audio_repository: IAudioRepository,
        audio_processor: IAudioProcessor,
    ) -> None:
        self._repository = audio_repository
        self._processor = audio_processor

    async def handle(self, query: SearchAudioQuery) -> List[SearchResultDTO]:
        """
        Handle semantic search query.

        Demonstrates:
        - Semantic search with embeddings
        - Advanced query patterns
        - Result ranking
        """
        # Generate query embedding
        query_embedding = await self._processor.generate_embeddings(query.query_text)

        # Search by embedding similarity
        user_id = UserId.from_str(query.user_id) if query.user_id else None
        results = await self._repository.search_by_embedding(
            embedding=query_embedding, limit=query.limit, user_id=user_id
        )

        # Map to DTOs
        return [
            SearchResultDTO(
                audio=AudioMapper.to_dto(audio), similarity_score=score, matched_segment=None
            )
            for audio, score in results
        ]
