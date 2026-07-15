"""Coupon business logic: validation and usage tracking."""

from decimal import Decimal

# Import timezone utilities for date and time handling.
from django.utils import timezone

from coupons.models import Coupon, CouponUsage


def validate_coupon(coupon, subtotal, user=None):
    """Validate a coupon for the given subtotal and user.

    Returns an error message string, or ``None`` when the coupon is valid.
    """

    # Check if the coupon is active.
    if not coupon.active:
        return 'This coupon is not active.'

    # Check if the coupon has expired.
    if coupon.is_expired:
        return 'This coupon has expired.'

    # Check if the subtotal meets the minimum amount.
    if coupon.min_amount and Decimal(str(subtotal)) < coupon.min_amount:
        return f'Minimum order amount is {coupon.min_amount}.'

    # Check if the coupon usage limit is reached.
    if coupon.usage_limit and coupon.used_count >= coupon.usage_limit:
        return 'This coupon has reached its usage limit.'

    # Check the user's personal coupon usage limit.
    if user is not None and user.is_authenticated and coupon.per_user_limit:

        # Count how many times this user used the coupon.
        used = CouponUsage.objects.filter(coupon=coupon, user=user).count()

        # Return error if user exceeded the limit.
        if used >= coupon.per_user_limit:
            return 'You have already used this coupon.'

    # Return None when the coupon is valid.
    return None


def apply_coupon_usage(coupon, user=None, order=None):
    """Record coupon usage and increment counters."""

    # Create a record of coupon usage.
    CouponUsage.objects.create(coupon=coupon, user=user, order=order)

    # Update total coupon usage count.
    coupon.used_count = CouponUsage.objects.filter(coupon=coupon).count()

    # Save only the updated usage count field.
    coupon.save(update_fields=['used_count'])
