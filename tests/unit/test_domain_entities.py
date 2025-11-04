"""Unit tests for domain entities."""

import pytest
from datetime import datetime, timezone, timedelta

from src.domain.entities.audio import Audio, AudioStatus
from src.domain.value_objects.audio_metadata import AudioFormat, AudioMetadata
from src.domain.value_objects.identifiers import AudioId, UserId, TranscriptionId


class TestAudioEntity:
    """Test Audio entity behavior."""

    @pytest.fixture
    def audio_metadata(self) -> AudioMetadata:
        """Create test audio metadata."""
        return AudioMetadata(
            duration=timedelta(seconds=120),
            sample_rate=44100,
            channels=2,
            bitrate=320000,
            format=AudioFormat.MP3,
        )

    @pytest.fixture
    def audio(self, audio_metadata: AudioMetadata) -> Audio:
        """Create test audio entity."""
        return Audio.create(
            user_id=UserId.generate(),
            filename="test.mp3",
            file_path="/storage/test.mp3",
            file_size=1024000,
            metadata=audio_metadata,
        )

    def test_create_audio_generates_id(self, audio_metadata: AudioMetadata) -> None:
        """Test that creating audio generates an ID."""
        audio = Audio.create(
            user_id=UserId.generate(),
            filename="test.mp3",
            file_path="/storage/test.mp3",
            file_size=1024000,
            metadata=audio_metadata,
        )

        assert audio.id is not None
        assert isinstance(audio.id, AudioId)

    def test_create_audio_sets_uploaded_status(self, audio: Audio) -> None:
        """Test that new audio has UPLOADED status."""
        assert audio.status == AudioStatus.UPLOADED

    def test_create_audio_raises_event(self, audio_metadata: AudioMetadata) -> None:
        """Test that creating audio raises AudioUploaded event."""
        audio = Audio.create(
            user_id=UserId.generate(),
            filename="test.mp3",
            file_path="/storage/test.mp3",
            file_size=1024000,
            metadata=audio_metadata,
        )

        events = audio.clear_events()
        assert len(events) == 1
        assert events[0].__class__.__name__ == "AudioUploaded"

    def test_add_transcription_changes_status(self, audio: Audio) -> None:
        """Test that adding transcription changes status to TRANSCRIBED."""
        audio.start_processing()
        audio.add_transcription(
            transcription_id=TranscriptionId.generate(),
            text="Test transcription",
            segments=[{"start": 0.0, "end": 1.0, "text": "Test"}],
            language="en",
            confidence=0.95,
        )

        assert audio.status == AudioStatus.TRANSCRIBED
        assert audio.transcription is not None
        assert audio.transcription.text == "Test transcription"

    def test_add_transcription_raises_event(self, audio: Audio) -> None:
        """Test that adding transcription raises event."""
        audio.start_processing()
        audio.clear_events()  # Clear previous events

        audio.add_transcription(
            transcription_id=TranscriptionId.generate(),
            text="Test transcription",
            segments=[],
            language="en",
            confidence=0.95,
        )

        events = audio.clear_events()
        assert len(events) == 1
        assert events[0].__class__.__name__ == "AudioTranscribed"

    def test_add_embeddings_changes_status_to_indexed(self, audio: Audio) -> None:
        """Test that adding embeddings changes status to INDEXED."""
        audio.start_processing()
        audio.add_transcription(
            transcription_id=TranscriptionId.generate(),
            text="Test",
            segments=[],
            language="en",
            confidence=0.95,
        )

        audio.add_embeddings([0.1, 0.2, 0.3])

        assert audio.status == AudioStatus.INDEXED
        assert audio.embedding_vector == [0.1, 0.2, 0.3]

    def test_add_embeddings_before_transcription_raises_error(self, audio: Audio) -> None:
        """Test that adding embeddings before transcription raises error."""
        with pytest.raises(ValueError, match="must be transcribed"):
            audio.add_embeddings([0.1, 0.2, 0.3])

    def test_mark_as_failed_sets_error_message(self, audio: Audio) -> None:
        """Test marking audio as failed."""
        audio.mark_as_failed("Test error")

        assert audio.status == AudioStatus.FAILED
        assert audio.error_message == "Test error"

    def test_is_processed_returns_true_when_indexed(self, audio: Audio) -> None:
        """Test is_processed property."""
        audio.start_processing()
        audio.add_transcription(
            transcription_id=TranscriptionId.generate(),
            text="Test",
            segments=[],
            language="en",
            confidence=0.95,
        )
        audio.add_embeddings([0.1, 0.2, 0.3])

        assert audio.is_processed is True

    def test_can_be_searched_requires_indexed_with_embeddings(self, audio: Audio) -> None:
        """Test can_be_searched property."""
        assert audio.can_be_searched is False

        audio.start_processing()
        audio.add_transcription(
            transcription_id=TranscriptionId.generate(),
            text="Test",
            segments=[],
            language="en",
            confidence=0.95,
        )
        audio.add_embeddings([0.1, 0.2, 0.3])

        assert audio.can_be_searched is True
