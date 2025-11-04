"""Audio-related domain events."""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from ..value_objects.identifiers import AudioId, TranscriptionId, UserId


class DomainEvent(Protocol):
    """Base protocol for domain events."""

    timestamp: datetime


@dataclass(frozen=True)
class AudioUploaded:
    """Event raised when audio is uploaded."""

    audio_id: AudioId
    user_id: UserId
    filename: str
    duration_seconds: float
    timestamp: datetime


@dataclass(frozen=True)
class AudioTranscribed:
    """Event raised when audio is transcribed."""

    audio_id: AudioId
    transcription_id: TranscriptionId
    text: str
    language: str
    confidence: float
    timestamp: datetime


@dataclass(frozen=True)
class EmbeddingsGenerated:
    """Event raised when embeddings are generated."""

    audio_id: AudioId
    vector_dimension: int
    timestamp: datetime


@dataclass(frozen=True)
class AudioProcessingFailed:
    """Event raised when audio processing fails."""

    audio_id: AudioId
    error_message: str
    timestamp: datetime
