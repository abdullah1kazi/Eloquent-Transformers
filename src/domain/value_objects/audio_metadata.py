"""Audio metadata value objects."""

from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
from typing import Optional


class AudioFormat(str, Enum):
    """Supported audio formats."""

    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    M4A = "m4a"
    OGG = "ogg"
    OPUS = "opus"


class AudioQuality(str, Enum):
    """Audio quality levels."""

    LOW = "low"  # < 64 kbps
    MEDIUM = "medium"  # 64-128 kbps
    HIGH = "high"  # 128-320 kbps
    LOSSLESS = "lossless"  # FLAC, WAV


@dataclass(frozen=True)
class AudioMetadata:
    """Immutable audio metadata value object."""

    duration: timedelta
    sample_rate: int
    channels: int
    bitrate: Optional[int]
    format: AudioFormat

    def __post_init__(self) -> None:
        """Validate audio metadata."""
        if self.duration.total_seconds() <= 0:
            raise ValueError("Duration must be positive")
        if self.sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        if self.channels not in (1, 2):
            raise ValueError("Channels must be 1 (mono) or 2 (stereo)")
        if self.bitrate is not None and self.bitrate <= 0:
            raise ValueError("Bitrate must be positive")

    @property
    def quality(self) -> AudioQuality:
        """Determine audio quality based on bitrate and format."""
        if self.format in (AudioFormat.FLAC, AudioFormat.WAV):
            return AudioQuality.LOSSLESS
        if self.bitrate is None:
            return AudioQuality.MEDIUM
        if self.bitrate < 64_000:
            return AudioQuality.LOW
        if self.bitrate < 128_000:
            return AudioQuality.MEDIUM
        return AudioQuality.HIGH

    @property
    def duration_seconds(self) -> float:
        """Get duration in seconds."""
        return self.duration.total_seconds()

    @property
    def is_high_quality(self) -> bool:
        """Check if audio is high quality."""
        return self.quality in (AudioQuality.HIGH, AudioQuality.LOSSLESS)


@dataclass(frozen=True)
class TranscriptionMetadata:
    """Metadata about transcription process."""

    language: str
    confidence: float
    model_version: str
    processing_time: timedelta

    def __post_init__(self) -> None:
        """Validate transcription metadata."""
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")
        if self.processing_time.total_seconds() < 0:
            raise ValueError("Processing time cannot be negative")

    @property
    def is_high_confidence(self) -> bool:
        """Check if transcription has high confidence."""
        return self.confidence >= 0.8
