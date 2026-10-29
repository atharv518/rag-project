"""
app/db/models/user.py

SQLAlchemy ORM model for the 'users' table.
Represents registered users in the platform. A user can exist independently
without belonging to any organization.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.membership import Membership
    from app.db.models.organization import Organization
    from app.db.models.document import Document
    from app.db.models.usage_record import UsageRecord


class User(Base, TimestampMixin):
    """User account entity.
    
    Can be an unassigned individual user or a member of one or more organizations.
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    full_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Relationships
    memberships: Mapped[list[Membership]] = relationship(
        "Membership",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    created_organizations: Mapped[list[Organization]] = relationship(
        "Organization",
        back_populates="creator",
        foreign_keys="Organization.created_by",
    )
    owned_documents: Mapped[list[Document]] = relationship(
        "Document",
        back_populates="owner_user",
        foreign_keys="Document.owner_user_id",
    )
    usage_records: Mapped[list[UsageRecord]] = relationship(
        "UsageRecord",
        back_populates="user",
    )

