"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class AudioUploadResponse(BaseModel):
    """Response for audio upload."""

    id: str
    filename: str
    status: str
    message: str


class TranscriptionSegment(BaseModel):
    """Transcription segment."""

    start: float = Field(..., description="Start time in seconds")
    end: float = Field(..., description="End time in seconds")
    text: str = Field(..., description="Transcribed text")


class TranscriptionResponse(BaseModel):
    """Response for transcription."""

    id: str
    text: str
    language: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    word_count: int
    segments: List[TranscriptionSegment]
    created_at: datetime


class AudioDetailResponse(BaseModel):
    """Detailed audio information."""

    id: str
    user_id: str
    filename: str
    file_size: int
    duration_seconds: float
    sample_rate: int
    format: str
    status: str
    created_at: datetime
    transcription: Optional[TranscriptionResponse] = None
    has_embeddings: bool


class AudioListResponse(BaseModel):
    """List of audio files."""

    items: List[AudioDetailResponse]
    total: int
    limit: int
    offset: int


class SearchRequest(BaseModel):
    """Semantic search request."""

    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    limit: int = Field(default=10, ge=1, le=100, description="Max results")

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate and clean query."""
        return v.strip()


class SearchResultResponse(BaseModel):
    """Search result item."""

    audio: AudioDetailResponse
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    matched_segment: Optional[TranscriptionSegment] = None


class SearchResponse(BaseModel):
    """Search results."""

    results: List[SearchResultResponse]
    query: str
    total: int


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    timestamp: datetime
    checks: dict


class ErrorResponse(BaseModel):
    """Error response."""

    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
