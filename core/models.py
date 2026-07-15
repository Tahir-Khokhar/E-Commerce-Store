"""Abstract base models shared across all applications."""

import uuid

from django.db import models


class BaseModel(models.Model):
    """Abstract base model with a UUID primary key and timestamps."""

    # Create a unique UUID primary key.
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Store the creation time automatically.
    created_at = models.DateTimeField(auto_now_add=True)

    # Update the modification time automatically.
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Prevent this model from creating a database table.
        abstract = True

        # Show newest records first.
        ordering = ('-created_at',)


class ActiveModel(BaseModel):
    """Abstract model adding an ``is_active`` flag."""

    # Store whether the record is active.
    is_active = models.BooleanField(default=True)

    class Meta:
        # Prevent this model from creating a database table.
        abstract = True

        # Show newest records first.
        ordering = ('-created_at',)
