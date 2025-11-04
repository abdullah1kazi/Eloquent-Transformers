"""Strongly-typed identifiers."""

from dataclasses import dataclass
from typing import NewType
from uuid import UUID, uuid4


@dataclass(frozen=True)
class AudioId:
    """Strongly-typed audio identifier."""

    value: UUID

    def __str__(self) -> str:
        """String representation."""
        return str(self.value)

    @classmethod
    def generate(cls) -> "AudioId":
        """Generate a new audio ID."""
        return cls(value=uuid4())

    @classmethod
    def from_str(cls, value: str) -> "AudioId":
        """Create from string."""
        return cls(value=UUID(value))


@dataclass(frozen=True)
class TranscriptionId:
    """Strongly-typed transcription identifier."""

    value: UUID

    def __str__(self) -> str:
        """String representation."""
        return str(self.value)

    @classmethod
    def generate(cls) -> "TranscriptionId":
        """Generate a new transcription ID."""
        return cls(value=uuid4())

    @classmethod
    def from_str(cls, value: str) -> "TranscriptionId":
        """Create from string."""
        return cls(value=UUID(value))


@dataclass(frozen=True)
class UserId:
    """Strongly-typed user identifier."""

    value: UUID

    def __str__(self) -> str:
        """String representation."""
        return str(self.value)

    @classmethod
    def generate(cls) -> "UserId":
        """Generate a new user ID."""
        return cls(value=uuid4())

    @classmethod
    def from_str(cls, value: str) -> "UserId":
        """Create from string."""
        return cls(value=UUID(value))


# Simple type aliases for string-based IDs
CorrelationId = NewType("CorrelationId", str)
SessionId = NewType("SessionId", str)
