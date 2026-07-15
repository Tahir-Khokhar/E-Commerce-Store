"""Project-wide constant values and choice tuples."""

from django.db import models
from django.utils.translation import gettext_lazy as _


# Order status lifecycle.
ORDER_STATUS_PENDING = 'pending'
ORDER_STATUS_PAID = 'paid'
ORDER_STATUS_PROCESSING = 'processing'
ORDER_STATUS_SHIPPED = 'shipped'
ORDER_STATUS_DELIVERED = 'delivered'
ORDER_STATUS_CANCELLED = 'cancelled'
ORDER_STATUS_REFUNDED = 'refunded'
ORDER_STATUS_CHOICES = (
    (ORDER_STATUS_PENDING, _('Pending')),
    (ORDER_STATUS_PAID, _('Paid')),
    (ORDER_STATUS_PROCESSING, _('Processing')),
    (ORDER_STATUS_SHIPPED, _('Shipped')),
    (ORDER_STATUS_DELIVERED, _('Delivered')),
    (ORDER_STATUS_CANCELLED, _('Cancelled')),
    (ORDER_STATUS_REFUNDED, _('Refunded')),
)


# Payment methods and statuses.
PAYMENT_METHOD_BANK = 'bank'
PAYMENT_METHOD_JAZZCASH = 'jazzcash'
PAYMENT_METHOD_COD = 'cod'

PAYMENT_METHOD_CHOICES = (
    (PAYMENT_METHOD_BANK, _('Bank account')),
    (PAYMENT_METHOD_JAZZCASH, _('JazzCash')),
    (PAYMENT_METHOD_COD, _('Cash on Delivery')),
)


PAYMENT_STATUS_PENDING = 'pending'
PAYMENT_STATUS_COMPLETED = 'completed'
PAYMENT_STATUS_FAILED = 'failed'
PAYMENT_STATUS_REFUNDED = 'refunded'
PAYMENT_STATUS_CHOICES = (
    (PAYMENT_STATUS_PENDING, _('Pending')),
    (PAYMENT_STATUS_COMPLETED, _('Completed')),
    (PAYMENT_STATUS_FAILED, _('Failed')),
    (PAYMENT_STATUS_REFUNDED, _('Refunded')),
)


# Coupon discount types.
COUPON_PERCENTAGE = 'percentage'
COUPON_FIXED = 'fixed'
COUPON_DISCOUNT_TYPE_CHOICES = (
    (COUPON_PERCENTAGE, _('Percentage')),
    (COUPON_FIXED, _('Fixed amount')),
)


# Refund request statuses.
REFUND_STATUS_PENDING = 'pending'
REFUND_STATUS_APPROVED = 'approved'
REFUND_STATUS_REJECTED = 'rejected'
REFUND_STATUS_CHOICES = (
    (REFUND_STATUS_PENDING, _('Pending')),
    (REFUND_STATUS_APPROVED, _('Approved')),
    (REFUND_STATUS_REJECTED, _('Rejected')),
)


# Notification types.
NOTIFICATION_ORDER = 'order'
NOTIFICATION_PAYMENT = 'payment'
NOTIFICATION_LOW_STOCK = 'low_stock'
NOTIFICATION_GENERAL = 'general'
NOTIFICATION_TYPE_CHOICES = (
    (NOTIFICATION_ORDER, _('Order')),
    (NOTIFICATION_PAYMENT, _('Payment')),
    (NOTIFICATION_LOW_STOCK, _('Low stock')),
    (NOTIFICATION_GENERAL, _('General')),
)


class ChoiceMeta(models.TextChoices):
    """Helper base for text choices when needed."""
