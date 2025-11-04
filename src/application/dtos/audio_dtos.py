"""DTOs for audio operations."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass(frozen=True)
class AudioDTO:
    """Audio data transfer object."""

    id: str
    user_id: str
    filename: str
    file_size: int
    duration_seconds: float
    sample_rate: int
    format: str
    status: str
    created_at: datetime
    transcription: Optional["TranscriptionDTO"] = None
    has_embeddings: bool = False


@dataclass(frozen=True)
class TranscriptionDTO:
    """Transcription data transfer object."""

    id: str
    text: str
    language: str
    confidence: float
    word_count: int
    created_at: datetime
    segments: List[dict]


@dataclass(frozen=True)
class SearchResultDTO:
    """Search result data transfer object."""

    audio: AudioDTO
    similarity_score: float
    matched_segment: Optional[dict] = None


@dataclass(frozen=True)
class AudioUploadResultDTO:
    """Result of audio upload operation."""

    audio_id: str
    filename: str
    status: str
    message: str
