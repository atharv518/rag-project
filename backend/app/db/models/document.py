"""
app/db/models/document.py

SQLAlchemy ORM model for the 'documents' table.
Tracks uploaded files, their storage references, processing status, and visibility scope.
"""

from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.document_chunk import DocumentChunk
    from app.db.models.organization import Organization
    from app.db.models.user import User


class DocumentStatus(str, enum.Enum):
    """Lifecycle statuses for document ingestion."""
    pending = "pending"
    processing = "processing"
    indexed = "indexed"
    failed = "failed"


class DocumentVisibility(str, enum.Enum):
    """Visibility scope of documents."""
    public = "public"
    personal = "personal"
    organization = "organization"


class Document(Base, TimestampMixin):
    """Document entity representing an uploaded knowledge file."""

    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    owner_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    storage_key: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
    )
    storage_bucket: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    file_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    file_size_bytes: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus, name="document_status_enum", native_enum=True),
        default=DocumentStatus.pending,
        nullable=False,
        index=True,
    )
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    visibility: Mapped[DocumentVisibility] = mapped_column(
        Enum(DocumentVisibility, name="document_visibility_enum", native_enum=True),
        default=DocumentVisibility.personal,
        nullable=False,
        index=True,
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationships
    organization: Mapped[Organization | None] = relationship(
        "Organization",
        back_populates="documents",
    )
    owner_user: Mapped[User | None] = relationship(
        "User",
        foreign_keys=[owner_user_id],
        back_populates="owned_documents",
    )
    chunks: Mapped[list[DocumentChunk]] = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
    )

