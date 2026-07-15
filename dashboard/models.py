"""Dashboard models: periodic metric snapshots for analytics."""

# Import Django ORM models and field definitions.
from django.db import models

# Import base model with common fields.
from core.models import BaseModel


class DashboardSnapshot(BaseModel):
    """Stores periodic dashboard metrics for admin views."""

    # Store a unique identifier for the snapshot.
    key = models.CharField(max_length=100, unique=True)

    # Store dashboard metrics as JSON data.
    value = models.JSONField(default=dict)

    class Meta:
        # Set the database table name.
        db_table = 'dashboard_snapshots'

        # Show latest snapshots first.
        ordering = ('-created_at',)

    def __str__(self):
        # Return the snapshot key as text.
        return self.key
