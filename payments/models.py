"""Payment models: stored payment records across gateways."""

# Import the uuid module for generating universally unique identifiers when needed.
import uuid

# Import Django's model classes to define database models and fields.
from django.db import models

# Import the shared base model that provides common fields and functionality.
from core.models import BaseModel

# Import payment-related constants used for field choices and default values.
from core.constants import (
    PAYMENT_METHOD_CHOICES,
    PAYMENT_STATUS_CHOICES,
    PAYMENT_STATUS_PENDING,
    PAYMENT_STATUS_COMPLETED,
)

# Import the custom validator to ensure numeric values are not negative.
from core.validators import validate_non_negative

# Import the custom User model for payment ownership.
from accounts.models import User

# Import the Order model that each payment is associated with.
from orders.models import Order


# Model representing a payment attempt or completed payment for an order.
class Payment(BaseModel):
    """A payment attempt/record for an order."""

    # Link the payment to its related order.
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='payments'
    )

    # Link the payment to the user who made it.
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='payments'
    )

    # Store the payment method using predefined choices.
    method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)

    # Store the payment amount and ensure it is non-negative.
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[validate_non_negative],
    )

    # Store the payment currency.
    currency = models.CharField(max_length=3, default='USD')

    # Store the current payment status.
    status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING
    )

    # Store the payment gateway transaction identifier.
    transaction_id = models.CharField(max_length=255, blank=True, db_index=True)

    # Store the total amount refunded for this payment.
    refunded_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Store the raw response returned by the payment gateway.
    gateway_response = models.TextField(blank=True)

    class Meta:
        # Order payments with the newest first.
        ordering = ('-created_at',)

        # Create a database index to speed up order and status lookups.
        indexes = [
            models.Index(fields=['order', 'status']),
        ]

    # Return a readable string representation of the payment.
    def __str__(self):
        return f'{self.method} {self.amount} - {self.status}'

    # Indicate whether the payment has been completed.
    @property
    def is_completed(self):
        return self.status == PAYMENT_STATUS_COMPLETED

    # Mark the payment as completed and update the related order if needed.
    def mark_completed(self, transaction_id=None):
        """Mark the payment completed and advance the order status."""

        # Update the payment status.
        self.status = PAYMENT_STATUS_COMPLETED

        # Store the transaction ID if one was provided.
        if transaction_id:
            self.transaction_id = transaction_id

        # Save the updated payment.
        self.save()

        # Advance the order status if it is still pending.
        if self.order.status == 'pending':
            self.order.set_status('paid', note=f'Paid via {self.method}')

    # Record a refund against this payment.
    def apply_refund(self, amount):
        """Record a refund against this payment."""

        # Increase the total refunded amount.
        self.refunded_amount += amount

        # Mark the payment as refunded when the full amount has been refunded.
        if self.refunded_amount >= self.amount:
            self.status = 'refunded'

        # Save the updated payment.
        self.save()
