"""Audio repository interface."""

from abc import ABC, abstractmethod

from ..entities.audio import Audio
from ..value_objects.identifiers import AudioId, UserId


class IAudioRepository(ABC):
    """Interface for audio repository (dependency inversion)."""

    @abstractmethod
    async def save(self, audio: Audio) -> None:
        """Save or update audio."""
        pass

    @abstractmethod
    async def find_by_id(self, audio_id: AudioId) -> Audio | None:
        """Find audio by ID."""
        pass

    @abstractmethod
    async def find_by_user(
        self, user_id: UserId, limit: int = 100, offset: int = 0
    ) -> list[Audio]:
        """Find all audio files for a user."""
        pass

    @abstractmethod
    async def delete(self, audio_id: AudioId) -> None:
        """Delete audio."""
        pass

    @abstractmethod
    async def search_by_text(
        self, query: str, limit: int = 10, user_id: UserId | None = None
    ) -> list[Audio]:
        """Full-text search on transcriptions."""
        pass

    @abstractmethod
    async def search_by_embedding(
        self, embedding: list[float], limit: int = 10, user_id: UserId | None = None
    ) -> list[tuple[Audio, float]]:
        """Semantic search using embedding similarity."""
        pass
