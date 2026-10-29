"""
app/db/models/usage_record.py

SQLAlchemy ORM model for the 'usage_records' table.
Tracks request and token consumption across guest, personal, and tenant requests.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.organization import Organization
    from app.db.models.user import User


class UsageRecord(Base):
    """Usage record tracking quotas and request volume."""

    __tablename__ = "usage_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    anonymous_identifier: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
    request_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    tokens_used: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    user: Mapped[User | None] = relationship(
        "User",
        back_populates="usage_records",
    )
    organization: Mapped[Organization | None] = relationship(
        "Organization",
        back_populates="usage_records",
    )

