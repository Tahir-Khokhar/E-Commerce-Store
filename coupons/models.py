"""Coupon models: percentage and fixed discounts with usage limits."""
# Import UUID utilities for generating unique identifiers.
import uuid
# Import Django ORM models and field definitions.
from django.db import models
# Import timezone utilities for date and time handling.
from django.utils import timezone
# Adds common model fields (UUID, timestamps)
from core.models import BaseModel
# Prevents negative numbers, Validates percentage values
from core.validators import validate_non_negative, validate_percentage
# Creates random coupon codes
from core.utils import generate_coupon_code
# Provides discount type options
from core.constants import COUPON_DISCOUNT_TYPE_CHOICES

from accounts.models import User


class Coupon(BaseModel):
    """A discount coupon with usage and validity constraints."""

    # Store a unique coupon code.
    code = models.CharField(max_length=30, unique=True, default=generate_coupon_code)

    # Store the discount type such as percentage or fixed amount.
    discount_type = models.CharField(
        max_length=10, choices=COUPON_DISCOUNT_TYPE_CHOICES,
        default='percentage',
    )

    # Store the discount value.
    value = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[validate_non_negative]
    )

    # Store the minimum order amount required for the coupon.
    min_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, validators=[validate_non_negative]
    )

    # Store the maximum discount limit.
    max_discount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        validators=[validate_non_negative],
    )

    # Store the maximum number of coupon uses.
    usage_limit = models.PositiveIntegerField(default=0, help_text='0 = unlimited')

    # Track how many times the coupon has been used.
    used_count = models.PositiveIntegerField(default=0)

    # Limit coupon usage per user.
    per_user_limit = models.PositiveIntegerField(default=0, help_text='0 = unlimited')

    # Enable or disable the coupon.
    active = models.BooleanField(default=True)

    # Store coupon start date and time.
    valid_from = models.DateTimeField(default=timezone.now)

    # Store coupon expiry date and time.
    valid_to = models.DateTimeField(null=True, blank=True)

    # Store optional coupon description.
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        # Display newest coupons first.
        ordering = ('-created_at',)

    def __str__(self):
        # Return coupon code as string representation.
        return self.code

    @property
    def is_expired(self):
        # Check whether the coupon is expired or not started.
        if self.valid_to and timezone.now() > self.valid_to:
            return True
        return timezone.now() < self.valid_from

    def calculate_discount(self, subtotal):
        """Return the discount amount for the given subtotal."""

        # Calculate percentage-based discount.
        if self.discount_type == 'percentage':
            discount = subtotal * (self.value / 100)
        else:
            # Use fixed discount amount.
            discount = self.value

        # Apply maximum discount limit if available.
        if self.max_discount is not None:
            discount = min(discount, self.max_discount)

        # Ensure discount does not exceed subtotal.
        return min(discount, subtotal)


class CouponUsage(BaseModel):
    """Record each time a coupon is applied to an order."""

    # Link the usage record to a coupon.
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE,
        related_name='usages'
    )

    # Link the usage record to a user.
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='coupon_usages'
    )

    # Link the usage record to an order.
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        related_name='coupon_usages'
    )

    def __str__(self):
        # Return coupon usage information as text.
        return f'{self.coupon.code} used by {self.user}'
