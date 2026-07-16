"""Wishlist models."""

# Import uuid for generating universally unique identifiers when needed.
import uuid

# Import Django's model classes for defining database models.
from django.db import models

# Import the shared base model that provides common fields and functionality.
from core.models import BaseModel

# Import the User model for wishlist ownership.
from accounts.models import User

# Import the Product model that can be added to a wishlist.
from products.models import Product


# Model representing a product saved to a user's wishlist.
class WishlistItem(BaseModel):
    """A product saved to a user's wishlist."""

    # Link the wishlist item to its owner.
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='wishlist'
    )

    # Link the wishlist item to the saved product.
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='wishlisted_by'
    )

    class Meta:
        # Display the newest wishlist items first.
        ordering = ('-created_at',)

        # Prevent the same user from adding the same product multiple times.
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'], name='unique_wishlist_item'
            )
        ]

    # Return a readable string representation of the wishlist item.
    def __str__(self):
        # Format the output using the user and product names.
        return f'{self.user} wants {self.product}'
