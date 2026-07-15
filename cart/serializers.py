# Serializers for the cart app.

from rest_framework import serializers  # Django REST Framework serializer classes.

# Import cart models.
from cart.models import Cart, CartItem

# Import product serializers.
from products.serializers import ProductSerializer, ProductVariantSerializer


# Serializer for displaying a cart item.
class CartItemSerializer(serializers.ModelSerializer):

    # Display product details instead of only the product ID.
    product = ProductSerializer(read_only=True)

    # Display variant details instead of only the variant ID.
    variant = ProductVariantSerializer(read_only=True)

    # Read-only field for the total price of this cart item.
    line_total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    class Meta:

        # Model used by this serializer.
        model = CartItem

        # Fields returned in the API response.
        fields = ('id', 'product', 'variant', 'quantity', 'line_total')


# Serializer used when adding or updating a cart item.
class CartItemCreateSerializer(serializers.ModelSerializer):

    # Product ID sent by the client.
    product_id = serializers.UUIDField(write_only=True)

    # Optional variant ID.
    # write_only=True hides it in API responses.
    # allow_null=True allows a null value.
    variant_id = serializers.UUIDField(
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:

        # Model used by this serializer.
        model = CartItem

        # Fields accepted from the client.
        fields = ('id', 'product_id', 'variant_id', 'quantity')


# Serializer for displaying the entire cart.
class CartSerializer(serializers.ModelSerializer):

    # Serialize all related cart items.
    # many=True means there can be multiple items.
    items = CartItemSerializer(many=True, read_only=True)

    # Total number of items in the cart.
    item_count = serializers.IntegerField(read_only=True)

    # Total price of all cart items.
    subtotal = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    class Meta:

        # Model used by this serializer.
        model = Cart

        # Fields returned in the API response.
        fields = (
            'id',
            'items',
            'item_count',
            'subtotal',
            'coupon',
            'created_at',
        )
