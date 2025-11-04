"""Domain service for audio processing orchestration."""

from abc import ABC, abstractmethod
from typing import List, Tuple

from ..entities.audio import Audio
from ..value_objects.audio_metadata import AudioMetadata


class IAudioProcessor(ABC):
    """Interface for audio processing service."""

    @abstractmethod
    async def extract_metadata(self, file_path: str) -> AudioMetadata:
        """Extract audio metadata from file."""
        pass

    @abstractmethod
    async def transcribe(self, audio: Audio) -> Tuple[str, List[dict], str, float]:
        """
        Transcribe audio to text.

        Returns:
            Tuple of (text, segments, language, confidence)
        """
        pass

    @abstractmethod
    async def generate_embeddings(self, text: str) -> List[float]:
        """Generate semantic embeddings from text."""
        pass

    @abstractmethod
    async def compute_audio_similarity(self, audio1: Audio, audio2: Audio) -> float:
        """Compute similarity between two audio files."""
        pass
