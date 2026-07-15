# Cart models: database-backed shopping carts with guest support.

import uuid  # Used for generating unique IDs (if needed).

from django.conf import settings  # Access Django project settings.
from django.db import models  # Provides Django model fields.

# Import the shared base model.
from core.models import BaseModel

# Import custom validator.
from core.validators import validate_positive

# Import related models.
from accounts.models import User
from products.models import Product, ProductVariant


# Represents a shopping cart.
class Cart(BaseModel):

    # Link the cart to a logged-in user (optional).
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,      # Delete the cart if the user is deleted.
        null=True,
        blank=True,
        related_name='carts'           # Access carts using user.carts.
    )

    # Store the guest user's session key.
    session_key = models.CharField(max_length=40, null=True, blank=True)

    # Optional coupon applied to the cart.
    coupon = models.ForeignKey(
        'coupons.Coupon',
        on_delete=models.SET_NULL,     # Keep the cart if the coupon is deleted.
        null=True,
        blank=True,
        related_name='carts'
    )

    class Meta:

        # Show newest carts first.
        ordering = ('-created_at',)

        # Database constraints.
        constraints = [

            # Ensure every cart has either a user or a session key.
            models.CheckConstraint(
                condition=models.Q(user__isnull=False) |
                          models.Q(session_key__isnull=False),
                name='cart_user_or_session',
            )

        ]

    # Human-readable representation.
    def __str__(self):
        return f'Cart {self.id}'

    # Create or retrieve a cart.
    @classmethod
    def get_or_create_cart(cls, user=None, session_key=None):

        # If the user is logged in, find or create their cart.
        if user and user.is_authenticated:

            # get_or_create() returns (object, created).
            cart, _ = cls.objects.get_or_create(user=user)

            return cart

        # Otherwise use the guest session.
        if session_key:

            cart, _ = cls.objects.get_or_create(session_key=session_key)

            return cart

        # Create a new empty cart.
        cart = cls.objects.create()

        return cart

    # Return all cart items.
    @property
    def items(self):

        # select_related() loads related objects in one database query.
        return self.cart_items.select_related('product', 'variant')

    # Return the total number of items.
    @property
    def item_count(self):

        # sum() adds all item quantities together.
        return sum(item.quantity for item in self.cart_items.all())

    # Return the subtotal price.
    @property
    def subtotal(self):

        # Sum the total price of every cart item.
        return sum(item.line_total for item in self.cart_items.all())

    # Add a product to the cart.
    def add_item(self, product, quantity=1, variant=None):

        # Find an existing cart item or create a new one.
        item, created = CartItem.objects.get_or_create(
            cart=self,
            product=product,
            variant=variant,
            defaults={'quantity': quantity},   # Used only when creating.
        )

        # Increase quantity if the item already exists.
        if not created:
            item.quantity += quantity
            item.save()

        return item

    # Remove all items from the cart.
    def clear(self):

        # Delete every related cart item.
        self.cart_items.all().delete()


# Represents a single item inside a cart.
class CartItem(BaseModel):

    # Link this item to a cart.
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )

    # Link this item to a product.
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )

    # Optional product variant (size, color, etc.).
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cart_items'
    )

    # Quantity must always be greater than zero.
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[validate_positive]
    )

    class Meta:

        # Show newest items first.
        ordering = ('-created_at',)

        # Prevent duplicate product/variant combinations in the same cart.
        constraints = [
            models.UniqueConstraint(
                fields=['cart', 'product', 'variant'],
                name='unique_cart_item',
            )
        ]

    # Human-readable representation.
    def __str__(self):
        return f'{self.quantity} x {self.product}'

    # Return the price of one item.
    @property
    def unit_price(self):

        # Use the variant price if available.
        if self.variant:
            return self.variant.effective_price

        # Otherwise use the product price.
        return self.product.price

    # Return the total price for this cart item.
    @property
    def line_total(self):

        # Multiply the unit price by the quantity.
        return self.unit_price * self.quantity
