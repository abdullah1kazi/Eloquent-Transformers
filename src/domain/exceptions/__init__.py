"""Domain-specific exceptions."""


class DomainException(Exception):
    """Base exception for domain errors."""

    pass


class AudioNotFoundException(DomainException):
    """Raised when audio is not found."""

    def __init__(self, audio_id: str) -> None:
        super().__init__(f"Audio not found: {audio_id}")
        self.audio_id = audio_id


class InvalidAudioFormatException(DomainException):
    """Raised when audio format is invalid."""

    def __init__(self, format: str) -> None:
        super().__init__(f"Invalid audio format: {format}")
        self.format = format


class TranscriptionFailedException(DomainException):
    """Raised when transcription fails."""

    def __init__(self, audio_id: str, reason: str) -> None:
        super().__init__(f"Transcription failed for {audio_id}: {reason}")
        self.audio_id = audio_id
        self.reason = reason


class UnauthorizedException(DomainException):
    """Raised when user is not authorized."""

    def __init__(self, message: str = "Unauthorized access") -> None:
        super().__init__(message)
