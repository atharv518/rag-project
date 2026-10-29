"""
app/db/base.py

SQLAlchemy declarative base and shared column mixins.

All ORM models in ``app/db/models/`` inherit from ``Base`` (which
registers them with SQLAlchemy's metadata) and optionally from
``TimestampMixin`` to get automatic ``created_at`` / ``updated_at``
columns.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Project-wide SQLAlchemy declarative base.

    Import this in every model module so that ``Base.metadata`` contains
    all table definitions (required by Alembic's autogenerate and
    ``create_all`` helpers).
    """


class TimestampMixin:
    """Adds ``created_at`` and ``updated_at`` audit columns to any model.

    Both columns are timezone-aware and default to the database's current
    timestamp.  ``updated_at`` is automatically updated on every row
    modification via the ``onupdate`` trigger (handled by SQLAlchemy at
    the Python layer; for database-level triggers see the Alembic
    migration).
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
