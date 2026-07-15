"""Serializers for the coupons app."""

# Import Django REST Framework serializer classes.
from rest_framework import serializers

from coupons.models import Coupon


class CouponSerializer(serializers.ModelSerializer):
    """Serialise a coupon."""

    class Meta:
        # Define the model connected to this serializer.
        model = Coupon

        # Specify fields included in API responses.
        fields = (
            'id', 'code', 'discount_type', 'value', 'min_amount',
            'max_discount', 'usage_limit', 'used_count', 'per_user_limit',
            'active', 'valid_from', 'valid_to', 'description', 'created_at',
        )

        # Prevent these fields from being edited through the API.
        read_only_fields = ('id', 'used_count', 'created_at')
