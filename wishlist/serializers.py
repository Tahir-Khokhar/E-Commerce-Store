"""Serializers for the wishlist app."""

# Import serializer classes used to convert data to and from JSON.
from rest_framework import serializers

# Import the WishlistItem model used by the serializers.
from wishlist.models import WishlistItem

# Import the ProductSerializer to include product details.
from products.serializers import ProductSerializer


# Serializer for WishlistItem model instances.
class WishlistItemSerializer(serializers.ModelSerializer):
    """Serialise a wishlist entry with product details."""

    # Include the related product as a nested read-only serializer.
    product = ProductSerializer(read_only=True)

    class Meta:
        # Specify the model this serializer is based on.
        model = WishlistItem

        # Define the fields included in the serialized output.
        fields = ('id', 'product', 'created_at')

        # Prevent these fields from being modified through the API.
        read_only_fields = ('id', 'created_at', 'product')


# Serializer for adding a product to the wishlist.
class AddWishlistSerializer(serializers.Serializer):
    """Serialise adding a product to the wishlist."""

    # Accept the product ID as a UUID value.
    product_id = serializers.UUIDField()
