"""Serializers for the notifications app."""

# Import serializer classes used to convert model instances to and from JSON.
from rest_framework import serializers

# Import the Notification model to be serialized.
from notifications.models import Notification


# Serializer for Notification model instances.
class NotificationSerializer(serializers.ModelSerializer):
    """Serialise a notification."""

    class Meta:
        # Specify the model this serializer is based on.
        model = Notification

        # Define the fields included in the serialized output.
        fields = ('id', 'type', 'title', 'message', 'link', 'read', 'created_at')

        # Mark these fields as read-only so they cannot be modified by clients.
        read_only_fields = ('id', 'created_at')
