"""Custom model managers used across the project."""

from django.db import models


class ActiveManager(models.Manager):
    """Return only active records by default."""

    def get_queryset(self):
        # Return only active records.
        return super().get_queryset().filter(is_active=True)


class FeaturedManager(models.Manager):
    """Return only featured, active records."""

    def get_queryset(self):
        # Return only active and featured records.
        return (
            super().get_queryset().filter(is_active=True, featured=True)
        )
