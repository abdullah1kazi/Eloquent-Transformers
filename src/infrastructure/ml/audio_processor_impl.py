"""Concrete implementation of audio processor."""

import asyncio
from datetime import timedelta
from typing import List, Tuple

import librosa

from ...domain.entities.audio import Audio
from ...domain.services.audio_processor import IAudioProcessor
from ...domain.value_objects.audio_metadata import AudioFormat, AudioMetadata
from .embedding_service import EmbeddingService
from .whisper_transcriber import WhisperTranscriber


class AudioProcessorImpl(IAudioProcessor):
    """
    Production-ready audio processor implementation.

    Demonstrates:
    - Dependency injection
    - Composition over inheritance
    - Async processing of CPU-bound tasks
    """

    def __init__(
        self,
        transcriber: WhisperTranscriber,
        embedding_service: EmbeddingService,
    ) -> None:
        self._transcriber = transcriber
        self._embedding_service = embedding_service

    async def extract_metadata(self, file_path: str) -> AudioMetadata:
        """Extract audio metadata using librosa."""

        def _extract() -> AudioMetadata:
            # Load audio file (librosa is CPU-bound)
            y, sr = librosa.load(file_path, sr=None)

            # Calculate duration
            duration = timedelta(seconds=float(len(y) / sr))

            # Get audio properties
            channels = 1 if len(y.shape) == 1 else y.shape[0]

            # Determine format from file extension
            import os

            ext = os.path.splitext(file_path)[1].lower().lstrip(".")
            try:
                audio_format = AudioFormat(ext)
            except ValueError:
                audio_format = AudioFormat.WAV  # Default fallback

            return AudioMetadata(
                duration=duration,
                sample_rate=int(sr),
                channels=channels,
                bitrate=None,  # Would need additional library to extract
                format=audio_format,
            )

        # Run in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _extract)

    async def transcribe(self, audio: Audio) -> Tuple[str, List[dict], str, float]:
        """Transcribe audio using Whisper."""
        return await self._transcriber.transcribe(audio.file_path)

    async def generate_embeddings(self, text: str) -> List[float]:
        """Generate semantic embeddings from text."""
        return await self._embedding_service.generate_embedding(text)

    async def compute_audio_similarity(self, audio1: Audio, audio2: Audio) -> float:
        """Compute similarity between two audio files based on embeddings."""
        if not audio1.embedding_vector or not audio2.embedding_vector:
            raise ValueError("Both audio files must have embeddings")

        return await self._embedding_service.compute_similarity(
            audio1.embedding_vector, audio2.embedding_vector
        )
