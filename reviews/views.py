"""Views and API endpoints for reviews."""

# Import get_object_or_404 to retrieve an object or automatically return a 404 error.
from django.shortcuts import get_object_or_404

# Import DRF permissions and viewsets for building API endpoints.
from rest_framework import permissions, viewsets

# Import action to define additional custom ViewSet actions when needed.
from rest_framework.decorators import action

# Import Response to return API responses.
from rest_framework.response import Response

# Import APIView for creating class-based API views.
from rest_framework.views import APIView

# Import the review models used by these API views.
from reviews.models import Review, ReviewHelpfulVote

# Import the serializers used for reading and writing review data.
from reviews.serializers import (
    ReviewCreateSerializer,
    ReviewSerializer,
    ReviewVoteSerializer,
)

# Import the Product model.
from products.models import Product


# ViewSet providing CRUD operations for product reviews.
class ReviewViewSet(viewsets.ModelViewSet):
    """API for product reviews."""

    # Default serializer for review responses.
    serializer_class = ReviewSerializer

    # Allow everyone to read reviews, but require authentication for modifications.
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    # Return the queryset used by this ViewSet.
    def get_queryset(self):
        # Load related user and product objects in the same query for better performance.
        queryset = Review.objects.select_related('user', 'product')

        # Retrieve the product slug from the query string.
        product_slug = self.request.query_params.get('product')

        # Filter reviews when a product slug is provided.
        if product_slug:
            queryset = queryset.filter(product__slug=product_slug, status='approved')

        # Return the final queryset.
        return queryset

    # Select the appropriate serializer based on the current action.
    def get_serializer_class(self):
        # Use the create serializer for write operations.
        if self.action in ('create', 'update', 'partial_update'):
            return ReviewCreateSerializer

        # Use the read serializer for all other actions.
        return ReviewSerializer

    # Handle additional logic after creating a review.
    def perform_create(self, serializer):
        # Save the review using the currently authenticated user.
        review = serializer.save(user=self.request.user)

        # Mark the review as a verified purchase if applicable.
        self._mark_verified(review)

    # Check whether the review qualifies as a verified purchase.
    def _mark_verified(self, review):
        # Import order models only when needed to avoid unnecessary imports.
        from orders.models import Order, OrderItem

        # Check whether the user has a qualifying completed order for this product.
        exists = OrderItem.objects.filter(
            order__user=review.user,
            order__status__in=('paid', 'processing', 'shipped', 'delivered'),
            product=review.product,
        ).exists()

        # Mark the review as verified if a matching order exists.
        if exists:
            review.is_verified_purchase = True

            # Save only the updated field.
            review.save(update_fields=['is_verified_purchase'])


# API view for toggling helpful votes on reviews.
class ReviewHelpfulAPIView(APIView):
    """Toggle the current user's helpful vote on a review."""

    # Only authenticated users can vote.
    permission_classes = (permissions.IsAuthenticated,)

    # Handle POST requests to add or remove a helpful vote.
    def post(self, request, pk):
        # Retrieve the requested review or return a 404 response.
        review = get_object_or_404(Review, pk=pk)

        # Create a vote if one doesn't exist, otherwise retrieve the existing vote.
        vote, created = ReviewHelpfulVote.objects.get_or_create(
            review=review, user=request.user
        )

        # Remove the vote if it already existed.
        if not created:
            vote.delete()

        # Update the cached helpful vote count.
        review.helpful_votes = review.votes.count()

        # Save only the updated helpful vote count.
        review.save(update_fields=['helpful_votes'])

        # Return the updated helpful vote total.
        return Response({'helpful_votes': review.helpful_votes})
