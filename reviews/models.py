"""Review models: product ratings, reviews and helpful votes."""

# Import uuid for generating universally unique identifiers when needed.
import uuid

# Import Django's model classes for defining database models.
from django.db import models

# Import gettext_lazy to support translation of user-facing text.
from django.utils.translation import gettext_lazy as _

# Import the shared base model that provides common fields and functionality.
from core.models import BaseModel

# Import the validator to ensure positive numeric values.
from core.validators import validate_positive

# Import the User model for review ownership.
from accounts.models import User

# Import the Product model that reviews belong to.
from products.models import Product


# Model representing a customer's review for a product.
class Review(BaseModel):
    """A customer review of a product."""

    # Define the available review approval statuses.
    STATUS_CHOICES = (
        # Mark a review as awaiting moderation.
        ('pending', _('Pending')),

        # Mark a review as approved and publicly visible.
        ('approved', _('Approved')),

        # Mark a review as rejected.
        ('rejected', _('Rejected')),
    )

    # Link each review to a product.
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='reviews'
    )

    # Link each review to the user who created it.
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews'
    )

    # Optionally link the review to an order.
    order = models.ForeignKey(
        'orders.Order', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reviews',
    )

    # Store the product rating and validate that it is positive.
    rating = models.PositiveSmallIntegerField(validators=[validate_positive])

    # Store the review title.
    title = models.CharField(max_length=150)

    # Store the review content.
    comment = models.TextField()

    # Store the moderation status of the review.
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    # Indicate whether the reviewer actually purchased the product.
    is_verified_purchase = models.BooleanField(default=False)

    # Store the total number of helpful votes received.
    helpful_votes = models.PositiveIntegerField(default=0)

    class Meta:
        # Display the newest reviews first.
        ordering = ('-created_at',)

        # Prevent a user from reviewing the same product more than once.
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'user'], name='unique_product_review'
            )
        ]

        # Create a database index to speed up product and status lookups.
        indexes = [
            models.Index(fields=['product', 'status']),
        ]

    # Return a readable string representation of the review.
    def __str__(self):
        # Format the review using the user, product, and rating.
        return f'{self.user} - {self.product} ({self.rating})'


# Model representing a helpful vote on a review.
class ReviewHelpfulVote(BaseModel):
    """Tracks which users marked a review as helpful (one vote each)."""

    # Link the vote to the reviewed product review.
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='votes'
    )

    # Link the vote to the user who cast it.
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='review_votes'
    )

    class Meta:
        # Ensure each user can vote only once per review.
        constraints = [
            models.UniqueConstraint(
                fields=['review', 'user'], name='unique_review_vote'
            )
        ]
