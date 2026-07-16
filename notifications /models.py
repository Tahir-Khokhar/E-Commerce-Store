"""Notification models: database notifications and email helpers."""

# Import Django's model classes to define database models and fields.
from django.db import models

# Import timezone utilities for working with date and time values.
from django.utils import timezone

# Import the shared base model that provides common model fields and behavior.
from core.models import BaseModel

# Import notification type constants and available choices.
from core.constants import NOTIFICATION_TYPE_CHOICES, NOTIFICATION_GENERAL

# Import the custom User model for notification ownership.
from accounts.models import User


# Model representing a notification for a specific user or a broadcast.
class Notification(BaseModel):
    """A persisted notification for a user (or a broadcast)."""

    # Associate the notification with a user. Null allows broadcast notifications.
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True,
        related_name='notifications',
    )

    # Store the notification type using predefined choices.
    type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPE_CHOICES, default=NOTIFICATION_GENERAL
    )

    # Store the notification title.
    title = models.CharField(max_length=200)

    # Store the main notification message.
    message = models.TextField()

    # Store an optional link related to the notification.
    link = models.CharField(max_length=255, blank=True)

    # Track whether the notification has been read.
    read = models.BooleanField(default=False)

    class Meta:
        # Order notifications with the newest first.
        ordering = ('-created_at',)

        # Create a database index to speed up user/read status lookups.
        indexes = [
            models.Index(fields=['user', 'read']),
        ]

    # Return the notification title as its string representation.
    def __str__(self):
        return self.title


# Model used to record low stock alerts for auditing purposes.
class LowStockAlert(BaseModel):
    """Record of a low-stock alert for auditing."""

    # Store the name of the product with low stock.
    product_name = models.CharField(max_length=200)

    # Store the product SKU if available.
    sku = models.CharField(max_length=100, blank=True)

    # Store the current stock quantity.
    current_stock = models.PositiveIntegerField(default=0)

    # Track whether the alert has been resolved.
    resolved = models.BooleanField(default=False)

    class Meta:
        # Order alerts with the newest first.
        ordering = ('-created_at',)

    # Return a readable description of the low stock alert.
    def __str__(self):
        return f'Low stock: {self.product_name} ({self.current_stock})'
