from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model

from store.models import Product, Variant

User = get_user_model()


class Address(models.Model):
    """Multiple addresses per user; Pakistan-specific cities/areas."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')

    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    phone = models.CharField(max_length=30)

    line1 = models.CharField(max_length=250)
    line2 = models.CharField(max_length=250, blank=True)

    city = models.CharField(max_length=80, blank=True)
    area = models.CharField(max_length=80, blank=True)

    postal_code = models.CharField(max_length=20, blank=True)

    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', '-id']

    def __str__(self):
        return f"{self.user.username} - {self.city} ({self.area})"


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        SHIPPED = 'SHIPPED', 'Shipped'
        DELIVERED = 'DELIVERED', 'Delivered'
        CANCELLED = 'CANCELLED', 'Cancelled'
        RETURNED = 'RETURNED', 'Returned'

    PAYMENT_METHOD_COD = 'COD'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    billing_address = models.ForeignKey(
        Address,
        on_delete=models.PROTECT,
        related_name='billing_orders',
        null=True,
        blank=True,
    )


    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    payment_method = models.CharField(max_length=10, default=PAYMENT_METHOD_COD)
    paid = models.BooleanField(default=False)

    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # keep legacy fields for now (migration backfill later)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'Order #{self.id} - {self.user.username}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    variant_size = models.ForeignKey(Variant, on_delete=models.PROTECT, related_name='order_items')

    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if not self.line_total:
            self.line_total = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
