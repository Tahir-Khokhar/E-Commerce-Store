"""Views and API endpoints for categories."""
# fetches a specific database object based on your query
from django.shortcuts import get_object_or_404, render
# Import DRF viewsets and filtering support.
from rest_framework import filters, viewsets
# grants unrestricted public access to an API endpoint
from rest_framework.permissions import AllowAny

from categories.models import Category
from categories.serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """CRUD API for categories."""

    # Retrieve all categories and load the parent in the same query.
    queryset = Category.objects.all().select_related('parent')

    # Serializer used to convert Category objects.
    serializer_class = CategorySerializer

    # Allow unrestricted access to this API.
    permission_classes = (AllowAny,)

    # Use the slug field to look up categories.
    lookup_field = 'slug'

    # Enable search and ordering support.
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)

    # Fields used for searching categories.
    search_fields = ('name', 'description')

    # Fields allowed for ordering results.
    ordering_fields = ('name', 'order')


def category_list(request):
    """Render a list of top-level categories."""

    # Get all active top-level categories.
    categories = Category.objects.filter(parent__isnull=True, is_active=True)

    # Render the category list template.
    return render(request, 'categories/list.html', {'categories': categories})


def category_detail(request, slug):
    """Render products within a category."""

    # Get the category or return a 404 page if it doesn't exist.
    category = get_object_or_404(Category, slug=slug, is_active=True)

    from products.models import Product

    # Get active products and load related data efficiently.
    products = Product.objects.filter(
        category=category, is_active=True
    ).select_related('brand').prefetch_related('images', 'tags')

    # Render the product list template with category data.
    return render(
        request,
        'products/list.html',
        {'category': category, 'products': products, 'title': category.name},
    )
