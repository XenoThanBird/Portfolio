"""
Base model with common mixins for UUID primary keys and timestamps.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class UUIDMixin:
    """Mixin providing a UUID primary key."""

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))


class TimestampMixin:
    """Mixin providing created_at and updated_at timestamps."""

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
