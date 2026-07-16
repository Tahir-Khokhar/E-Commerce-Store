"""Serializers for the reviews app."""

# Import serializer classes used to convert model instances to and from JSON.
from rest_framework import serializers

# Import the review-related models used by the serializers.
from reviews.models import Review, ReviewHelpfulVote

# Import the user serializer to include review author information.
from accounts.serializers import UserSerializer


# Serializer for Review model instances.
class ReviewSerializer(serializers.ModelSerializer):
    """Serialise a review with its author."""

    # Include the related user as a nested read-only serializer.
    user = UserSerializer(read_only=True)

    class Meta:
        # Specify the model this serializer is based on.
        model = Review

        # Define the fields included in the serialized output.
        fields = (
            'id', 'product', 'user', 'rating', 'title', 'comment',
            'status', 'is_verified_purchase', 'helpful_votes', 'created_at',
        )

        # Prevent these fields from being modified through the API.
        read_only_fields = (
            'id', 'user', 'status', 'is_verified_purchase',
            'helpful_votes', 'created_at',
        )


# Serializer for creating or updating reviews.
class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serialise review creation."""

    class Meta:
        # Specify the model this serializer is based on.
        model = Review

        # Define the fields accepted during review creation.
        fields = ('id', 'product', 'rating', 'title', 'comment')

    # Validate that the rating falls within the allowed range.
    def validate_rating(self, value):
        # Reject ratings outside the range of 1 to 5.
        if not (1 <= value <= 5):
            raise serializers.ValidationError('Rating must be between 1 and 5.')

        # Return the validated rating.
        return value

    # Create a new review or update an existing one for the same user and product.
    def create(self, validated_data):
        # Retrieve the current request from the serializer context.
        request = self.context['request']

        # Create a new review or update the existing one if it already exists.
        review, _ = Review.objects.update_or_create(
            product=validated_data['product'],
            user=request.user,
            defaults={
                'rating': validated_data['rating'],
                'title': validated_data['title'],
                'comment': validated_data['comment'],
            },
        )

        # Return the created or updated review.
        return review


# Serializer for ReviewHelpfulVote model instances.
class ReviewVoteSerializer(serializers.ModelSerializer):
    """Serialise a helpful vote toggle."""

    class Meta:
        # Specify the model this serializer is based on.
        model = ReviewHelpfulVote

        # Define the fields included in the serialized output.
        fields = ('id', 'review', 'user', 'created_at')

        # Prevent these fields from being modified through the API.
        read_only_fields = ('id', 'user', 'created_at')
