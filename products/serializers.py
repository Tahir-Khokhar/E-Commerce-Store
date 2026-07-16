"""Serializers for the products app."""

# Import serializer classes used to convert model instances to and from JSON.
from rest_framework import serializers

# Import the product-related models used by the serializers.
from products.models import (
    Attribute,
    AttributeValue,
    Brand,
    Product,
    ProductImage,
    ProductVariant,
    Tag,
)


# Serializer for Brand model instances.
class BrandSerializer(serializers.ModelSerializer):
    """Serialise a brand."""

    class Meta:
        # Specify the model this serializer is based on.
        model = Brand

        # Define the fields included in the serialized output.
        fields = ('id', 'name', 'slug', 'logo', 'description', 'website', 'is_active')


# Serializer for Tag model instances.
class TagSerializer(serializers.ModelSerializer):
    """Serialise a tag."""

    class Meta:
        # Specify the model this serializer is based on.
        model = Tag

        # Define the fields included in the serialized output.
        fields = ('id', 'name', 'slug')


# Serializer for ProductImage model instances.
class ProductImageSerializer(serializers.ModelSerializer):
    """Serialise a product image."""

    class Meta:
        # Specify the model this serializer is based on.
        model = ProductImage

        # Define the fields included in the serialized output.
        fields = ('id', 'image', 'alt', 'is_primary', 'order')


# Serializer for AttributeValue model instances.
class AttributeValueSerializer(serializers.ModelSerializer):
    """Serialise an attribute value."""

    class Meta:
        # Specify the model this serializer is based on.
        model = AttributeValue

        # Define the fields included in the serialized output.
        fields = ('id', 'attribute', 'value', 'slug')


# Serializer for ProductVariant model instances.
class ProductVariantSerializer(serializers.ModelSerializer):
    """Serialise a product variant."""

    # Include related attribute values as nested read-only data.
    attribute_values = AttributeValueSerializer(many=True, read_only=True)

    # Expose the computed effective price as a read-only decimal field.
    effective_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        # Specify the model this serializer is based on.
        model = ProductVariant

        # Define the fields included in the serialized output.
        fields = (
            'id', 'name', 'sku', 'barcode', 'price', 'effective_price',
            'stock', 'attribute_values', 'is_active',
        )


# Serializer for Product model instances with related data.
class ProductSerializer(serializers.ModelSerializer):
    """Serialise a product with related data."""

    # Include related product images as nested read-only data.
    images = ProductImageSerializer(many=True, read_only=True)

    # Include the related brand as nested read-only data.
    brand = BrandSerializer(read_only=True)

    # Represent the related category using its slug.
    category = serializers.SlugRelatedField(slug_field='slug', read_only=True)

    # Include related tags as nested read-only data.
    tags = TagSerializer(many=True, read_only=True)

    # Expose the average rating using a custom serializer method.
    average_rating = serializers.SerializerMethodField()

    # Expose the review count using a custom serializer method.
    review_count = serializers.SerializerMethodField()

    # Include related product variants as nested read-only data.
    variants = ProductVariantSerializer(many=True, read_only=True)

    # Expose whether the product is currently on sale.
    on_sale = serializers.BooleanField(read_only=True)

    # Expose the calculated discount percentage.
    discount_percent = serializers.FloatField(read_only=True)

    class Meta:
        # Specify the model this serializer is based on.
        model = Product

        # Define the fields included in the serialized output.
        fields = (
            'id', 'name', 'slug', 'short_description', 'description',
            'category', 'brand', 'tags', 'price', 'compare_at_price',
            'sku', 'barcode', 'stock', 'weight', 'featured', 'is_new',
            'best_seller', 'images', 'variants', 'average_rating',
            'review_count', 'on_sale', 'discount_percent', 'created_at',
        )

    # Return the average rating for the product.
    def get_average_rating(self, obj):
        # Safely retrieve the annotated average rating if it exists.
        value = getattr(obj, 'avg_rating', None)

        # Return the model property if no annotated value is available.
        if value is None:
            return obj.average_rating

        # Round the annotated rating to two decimal places for consistency.
        return round(value, 2)

    # Return the review count for the product.
    def get_review_count(self, obj):
        # Safely retrieve the annotated review count, otherwise use the model property.
        return getattr(obj, 'num_reviews', obj.review_count)


# Serializer for creating Product model instances.
class ProductCreateSerializer(serializers.ModelSerializer):
    """Serialise product creation including nested write support."""

    class Meta:
        # Specify the model this serializer is based on.
        model = Product

        # Define the fields accepted during product creation.
        fields = (
            'id', 'name', 'short_description', 'description', 'category',
            'brand', 'price', 'compare_at_price', 'sku', 'barcode',
            'stock', 'track_inventory', 'weight', 'featured', 'is_new',
            'best_seller', 'meta_title', 'meta_description',
        )
