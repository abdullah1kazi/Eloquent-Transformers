"""Command for uploading audio files."""

from dataclasses import dataclass
from typing import BinaryIO

from ..dtos.audio_dtos import AudioUploadResultDTO
from ...domain.repositories.audio_repository import IAudioRepository
from ...domain.services.audio_processor import IAudioProcessor
from ...domain.entities.audio import Audio
from ...domain.value_objects.identifiers import UserId


@dataclass
class UploadAudioCommand:
    """Command to upload audio file."""

    user_id: str
    filename: str
    file: BinaryIO
    content_type: str


class UploadAudioCommandHandler:
    """Handler for audio upload command."""

    def __init__(
        self,
        audio_repository: IAudioRepository,
        audio_processor: IAudioProcessor,
        storage_path: str,
    ) -> None:
        self._repository = audio_repository
        self._processor = audio_processor
        self._storage_path = storage_path

    async def handle(self, command: UploadAudioCommand) -> AudioUploadResultDTO:
        """
        Handle audio upload command.

        This demonstrates the Command pattern in CQRS architecture.
        Commands change state and return minimal data.
        """
        import os
        import aiofiles
        from uuid import uuid4

        # Generate unique file path
        file_id = str(uuid4())
        file_extension = os.path.splitext(command.filename)[1]
        file_path = os.path.join(self._storage_path, f"{file_id}{file_extension}")

        # Save file to storage
        async with aiofiles.open(file_path, "wb") as f:
            content = command.file.read()
            await f.write(content)
            file_size = len(content)

        # Extract metadata
        metadata = await self._processor.extract_metadata(file_path)

        # Create domain entity
        audio = Audio.create(
            user_id=UserId.from_str(command.user_id),
            filename=command.filename,
            file_path=file_path,
            file_size=file_size,
            metadata=metadata,
        )

        # Persist to repository
        await self._repository.save(audio)

        # Publish domain events (would be handled by event bus in production)
        events = audio.clear_events()
        # TODO: Publish events to message queue

        return AudioUploadResultDTO(
            audio_id=str(audio.id),
            filename=audio.filename,
            status=audio.status.value,
            message="Audio uploaded successfully",
        )
