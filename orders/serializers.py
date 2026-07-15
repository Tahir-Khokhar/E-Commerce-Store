# Serializers for the categories app.

from rest_framework import serializers  # Django REST Framework serializer classes.

# Import the Category model.
from categories.models import Category


# Serializer for category data.
class CategorySerializer(serializers.ModelSerializer):

    # SerializerMethodField calls a custom method to generate the value.
    children = serializers.SerializerMethodField()

    # Return the number of active products in the category.
    products_count = serializers.SerializerMethodField()

    class Meta:

        # Model used by this serializer.
        model = Category

        # Fields included in the API response.
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'parent',
            'image',
            'order',
            'is_active',
            'meta_title',
            'meta_description',
            'children',
            'products_count',
        )

        # These fields cannot be modified by the client.
        read_only_fields = (
            'id',
            'slug',
            'children',
            'products_count',
        )

    # Return all active child categories.
    def get_children(self, obj):

        # Filter only active child categories.
        children = obj.children.filter(is_active=True)

        # Serialize the child categories.
        # many=True means there can be multiple child categories.
        return CategorySerializer(
            children,
            many=True,
            context=self.context
        ).data

    # Return the number of active products in this category.
    def get_products_count(self, obj):

        # count() returns the total number of matching records.
        return obj.products.filter(is_active=True).count()
