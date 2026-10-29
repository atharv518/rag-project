"""
app/db/models/organization.py

SQLAlchemy ORM model for the 'organizations' table.
Represents a multi-tenant organization or enterprise account.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.membership import Membership
    from app.db.models.user import User
    from app.db.models.document import Document
    from app.db.models.usage_record import UsageRecord


class Organization(Base, TimestampMixin):
    """Tenant organization entity."""

    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    creator: Mapped[User | None] = relationship(
        "User",
        back_populates="created_organizations",
        foreign_keys=[created_by],
    )
    memberships: Mapped[list[Membership]] = relationship(
        "Membership",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    documents: Mapped[list[Document]] = relationship(
        "Document",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    usage_records: Mapped[list[UsageRecord]] = relationship(
        "UsageRecord",
        back_populates="organization",
    )

