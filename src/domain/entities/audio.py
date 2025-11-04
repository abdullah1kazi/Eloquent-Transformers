"""Audio aggregate root."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from ..events.audio_events import (
    AudioTranscribed,
    AudioUploaded,
    EmbeddingsGenerated,
)
from ..value_objects.audio_metadata import AudioMetadata
from ..value_objects.identifiers import AudioId, TranscriptionId, UserId


class AudioStatus(str, Enum):
    """Audio processing status."""

    UPLOADED = "uploaded"
    PROCESSING = "processing"
    TRANSCRIBED = "transcribed"
    INDEXED = "indexed"
    FAILED = "failed"


@dataclass
class Transcription:
    """Transcription entity."""

    id: TranscriptionId
    text: str
    segments: List[dict]
    language: str
    confidence: float
    created_at: datetime

    def get_segment_at_time(self, seconds: float) -> Optional[dict]:
        """Get transcription segment at specific time."""
        for segment in self.segments:
            if segment["start"] <= seconds <= segment["end"]:
                return segment
        return None


@dataclass
class Audio:
    """Audio aggregate root - main entity with rich behavior."""

    id: AudioId
    user_id: UserId
    filename: str
    file_path: str
    file_size: int
    metadata: AudioMetadata
    status: AudioStatus
    created_at: datetime
    updated_at: datetime
    transcription: Optional[Transcription] = None
    embedding_vector: Optional[List[float]] = None
    error_message: Optional[str] = None
    _events: List[object] = field(default_factory=list, init=False, repr=False)

    @classmethod
    def create(
        cls,
        user_id: UserId,
        filename: str,
        file_path: str,
        file_size: int,
        metadata: AudioMetadata,
    ) -> "Audio":
        """Factory method to create new audio."""
        now = datetime.now(timezone.utc)
        audio = cls(
            id=AudioId.generate(),
            user_id=user_id,
            filename=filename,
            file_path=file_path,
            file_size=file_size,
            metadata=metadata,
            status=AudioStatus.UPLOADED,
            created_at=now,
            updated_at=now,
        )
        audio._add_event(
            AudioUploaded(
                audio_id=audio.id,
                user_id=user_id,
                filename=filename,
                duration_seconds=metadata.duration_seconds,
                timestamp=now,
            )
        )
        return audio

    def add_transcription(
        self,
        transcription_id: TranscriptionId,
        text: str,
        segments: List[dict],
        language: str,
        confidence: float,
    ) -> None:
        """Add transcription to audio."""
        if self.status == AudioStatus.FAILED:
            raise ValueError("Cannot add transcription to failed audio")

        now = datetime.now(timezone.utc)
        self.transcription = Transcription(
            id=transcription_id,
            text=text,
            segments=segments,
            language=language,
            confidence=confidence,
            created_at=now,
        )
        self.status = AudioStatus.TRANSCRIBED
        self.updated_at = now

        self._add_event(
            AudioTranscribed(
                audio_id=self.id,
                transcription_id=transcription_id,
                text=text,
                language=language,
                confidence=confidence,
                timestamp=now,
            )
        )

    def add_embeddings(self, embedding_vector: List[float]) -> None:
        """Add embedding vector to audio."""
        if self.status != AudioStatus.TRANSCRIBED:
            raise ValueError("Audio must be transcribed before adding embeddings")

        self.embedding_vector = embedding_vector
        self.status = AudioStatus.INDEXED
        self.updated_at = datetime.now(timezone.utc)

        self._add_event(
            EmbeddingsGenerated(
                audio_id=self.id,
                vector_dimension=len(embedding_vector),
                timestamp=datetime.now(timezone.utc),
            )
        )

    def mark_as_failed(self, error_message: str) -> None:
        """Mark audio processing as failed."""
        self.status = AudioStatus.FAILED
        self.error_message = error_message
        self.updated_at = datetime.now(timezone.utc)

    def start_processing(self) -> None:
        """Start audio processing."""
        if self.status != AudioStatus.UPLOADED:
            raise ValueError(f"Cannot process audio in status {self.status}")
        self.status = AudioStatus.PROCESSING
        self.updated_at = datetime.now(timezone.utc)

    @property
    def is_processed(self) -> bool:
        """Check if audio is fully processed."""
        return self.status == AudioStatus.INDEXED

    @property
    def can_be_searched(self) -> bool:
        """Check if audio can be searched."""
        return self.status == AudioStatus.INDEXED and self.embedding_vector is not None

    def _add_event(self, event: object) -> None:
        """Add domain event."""
        self._events.append(event)

    def clear_events(self) -> List[object]:
        """Clear and return domain events."""
        events = self._events.copy()
        self._events.clear()
        return events
