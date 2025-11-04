"""Command for transcribing audio."""

from dataclasses import dataclass

from ..dtos.audio_dtos import TranscriptionDTO
from ...domain.repositories.audio_repository import IAudioRepository
from ...domain.services.audio_processor import IAudioProcessor
from ...domain.value_objects.identifiers import AudioId, TranscriptionId
from ...domain.exceptions import AudioNotFoundException


@dataclass
class TranscribeAudioCommand:
    """Command to transcribe audio."""

    audio_id: str
    language: str = "auto"  # Auto-detect language


class TranscribeAudioCommandHandler:
    """Handler for audio transcription command."""

    def __init__(
        self,
        audio_repository: IAudioRepository,
        audio_processor: IAudioProcessor,
    ) -> None:
        self._repository = audio_repository
        self._processor = audio_processor

    async def handle(self, command: TranscribeAudioCommand) -> TranscriptionDTO:
        """
        Handle audio transcription command.

        Demonstrates:
        - Command pattern
        - Domain service usage
        - Repository pattern
        - Domain event generation
        """
        # Fetch audio aggregate
        audio_id = AudioId.from_str(command.audio_id)
        audio = await self._repository.find_by_id(audio_id)

        if not audio:
            raise AudioNotFoundException(command.audio_id)

        # Mark as processing
        audio.start_processing()
        await self._repository.save(audio)

        try:
            # Perform transcription (domain service)
            text, segments, language, confidence = await self._processor.transcribe(audio)

            # Update aggregate with transcription
            transcription_id = TranscriptionId.generate()
            audio.add_transcription(
                transcription_id=transcription_id,
                text=text,
                segments=segments,
                language=language,
                confidence=confidence,
            )

            # Generate embeddings
            embeddings = await self._processor.generate_embeddings(text)
            audio.add_embeddings(embeddings)

            # Persist changes
            await self._repository.save(audio)

            # Publish domain events
            events = audio.clear_events()
            # TODO: Publish to event bus

            return TranscriptionDTO(
                id=str(transcription_id),
                text=text,
                language=language,
                confidence=confidence,
                word_count=len(text.split()),
                created_at=audio.transcription.created_at,
                segments=segments,
            )

        except Exception as e:
            # Mark as failed
            audio.mark_as_failed(str(e))
            await self._repository.save(audio)
            raise
