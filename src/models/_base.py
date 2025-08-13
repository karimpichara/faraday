# Base model for all models
# Contains id, uuid, created_at, updated_at, active

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime


class ToDictMixin:
    """Mixin class to add to_dict functionality to SQLAlchemy models."""

    def to_dict(self) -> dict[str, Any]:
        """Convert SQLAlchemy model instance to dictionary."""
        row_to_dict = self.__dict__.copy()
        if "_sa_instance_state" in row_to_dict:
            del row_to_dict["_sa_instance_state"]
        return row_to_dict


# Import db after mixin definition to avoid circular imports
from src.models import db  # noqa: E402


class BaseModel(db.Model, ToDictMixin):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(
        db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )
    created_at = db.Column(DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )
    active = db.Column(Boolean, nullable=False, default=True, index=True)

    @classmethod
    def active_records(cls):
        """Return query filtered to only active records."""
        return cls.query.filter_by(active=True)

    def soft_delete(self) -> None:
        """Mark this record as inactive (soft delete)."""
        self.active = False
        self.updated_at = datetime.now()

    def restore(self) -> None:
        """Mark this record as active (restore from soft delete)."""
        self.active = True
        self.updated_at = datetime.now()
