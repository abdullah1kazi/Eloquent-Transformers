"""SQLAlchemy models for database persistence."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import JSON, Column, DateTime, Enum, Float, Integer, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ARRAY
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all models."""

    pass


class AudioModel(Base):
    """SQLAlchemy model for Audio entity."""

    __tablename__ = "audios"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)

    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)

    # Metadata (denormalized for performance)
    duration_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    sample_rate: Mapped[int] = mapped_column(Integer, nullable=False)
    channels: Mapped[int] = mapped_column(Integer, nullable=False)
    bitrate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    format: Mapped[str] = mapped_column(String(10), nullable=False)

    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Embedding vector (for semantic search)
    embedding_vector: Mapped[Optional[list]] = mapped_column(ARRAY(Float), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    transcription: Mapped[Optional["TranscriptionModel"]] = relationship(
        "TranscriptionModel", back_populates="audio", uselist=False, cascade="all, delete-orphan"
    )


class TranscriptionModel(Base):
    """SQLAlchemy model for Transcription entity."""

    __tablename__ = "transcriptions"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    audio_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("audios.id", ondelete="CASCADE"), nullable=False
    )

    text: Mapped[str] = mapped_column(Text, nullable=False)
    segments: Mapped[dict] = mapped_column(JSON, nullable=False)
    language: Mapped[str] = mapped_column(String(10), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    audio: Mapped[AudioModel] = relationship("AudioModel", back_populates="transcription")
