"""Unit tests for value objects."""

import pytest
from datetime import timedelta

from src.domain.value_objects.audio_metadata import (
    AudioFormat,
    AudioMetadata,
    AudioQuality,
    TranscriptionMetadata,
)


class TestAudioMetadata:
    """Test AudioMetadata value object."""

    def test_create_valid_metadata(self) -> None:
        """Test creating valid audio metadata."""
        metadata = AudioMetadata(
            duration=timedelta(seconds=120),
            sample_rate=44100,
            channels=2,
            bitrate=320000,
            format=AudioFormat.MP3,
        )

        assert metadata.duration_seconds == 120.0
        assert metadata.sample_rate == 44100
        assert metadata.channels == 2

    def test_invalid_duration_raises_error(self) -> None:
        """Test that invalid duration raises error."""
        with pytest.raises(ValueError, match="Duration must be positive"):
            AudioMetadata(
                duration=timedelta(seconds=0),
                sample_rate=44100,
                channels=2,
                bitrate=None,
                format=AudioFormat.MP3,
            )

    def test_invalid_sample_rate_raises_error(self) -> None:
        """Test that invalid sample rate raises error."""
        with pytest.raises(ValueError, match="Sample rate must be positive"):
            AudioMetadata(
                duration=timedelta(seconds=120),
                sample_rate=0,
                channels=2,
                bitrate=None,
                format=AudioFormat.MP3,
            )

    def test_invalid_channels_raises_error(self) -> None:
        """Test that invalid channels raises error."""
        with pytest.raises(ValueError, match="Channels must be"):
            AudioMetadata(
                duration=timedelta(seconds=120),
                sample_rate=44100,
                channels=3,  # Invalid
                bitrate=None,
                format=AudioFormat.MP3,
            )

    def test_quality_determination_high(self) -> None:
        """Test quality determination for high bitrate."""
        metadata = AudioMetadata(
            duration=timedelta(seconds=120),
            sample_rate=44100,
            channels=2,
            bitrate=320000,
            format=AudioFormat.MP3,
        )

        assert metadata.quality == AudioQuality.HIGH
        assert metadata.is_high_quality is True

    def test_quality_determination_lossless(self) -> None:
        """Test quality determination for lossless formats."""
        metadata = AudioMetadata(
            duration=timedelta(seconds=120),
            sample_rate=44100,
            channels=2,
            bitrate=None,
            format=AudioFormat.FLAC,
        )

        assert metadata.quality == AudioQuality.LOSSLESS
        assert metadata.is_high_quality is True

    def test_immutability(self) -> None:
        """Test that audio metadata is immutable."""
        metadata = AudioMetadata(
            duration=timedelta(seconds=120),
            sample_rate=44100,
            channels=2,
            bitrate=None,
            format=AudioFormat.MP3,
        )

        with pytest.raises(Exception):  # dataclass frozen=True raises FrozenInstanceError
            metadata.sample_rate = 48000  # type: ignore


class TestTranscriptionMetadata:
    """Test TranscriptionMetadata value object."""

    def test_create_valid_metadata(self) -> None:
        """Test creating valid transcription metadata."""
        metadata = TranscriptionMetadata(
            language="en",
            confidence=0.95,
            model_version="whisper-base",
            processing_time=timedelta(seconds=5),
        )

        assert metadata.language == "en"
        assert metadata.confidence == 0.95

    def test_invalid_confidence_raises_error(self) -> None:
        """Test that invalid confidence raises error."""
        with pytest.raises(ValueError, match="Confidence must be between"):
            TranscriptionMetadata(
                language="en",
                confidence=1.5,  # Invalid
                model_version="whisper-base",
                processing_time=timedelta(seconds=5),
            )

    def test_is_high_confidence(self) -> None:
        """Test high confidence check."""
        high = TranscriptionMetadata(
            language="en",
            confidence=0.9,
            model_version="whisper-base",
            processing_time=timedelta(seconds=5),
        )

        low = TranscriptionMetadata(
            language="en",
            confidence=0.7,
            model_version="whisper-base",
            processing_time=timedelta(seconds=5),
        )

        assert high.is_high_confidence is True
        assert low.is_high_confidence is False
