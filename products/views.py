"""Views and API endpoints for products."""

# Paginator: Django's built-in helper to split a queryset into paginated pages
from django.core.paginator import Paginator
# Avg/Count: Django ORM aggregate functions used to compute rating stats; Q enables OR queries
from django.db.models import Avg, Count, Q
# get_object_or_404: returns a 404 if the lookup fails; render: renders a template with a context dict
from django.shortcuts import get_object_or_404, render

# filters: DRF search/ordering filter backends; viewsets: base class for the API view
from rest_framework import filters, viewsets
# AllowAny: permission class that permits unauthenticated access to the API
from rest_framework.permissions import AllowAny

# Domain models used by the views
from products.models import (
    Brand,
    Product,
    ProductImage,
    ProductVariant,
)
# Serializers that convert Product models to/from JSON for the API
from products.serializers import (
    ProductCreateSerializer,
    ProductSerializer,
)
# Review model used to display approved product reviews on the detail page
from reviews.models import Review


class ProductViewSet(viewsets.ModelViewSet):
    """CRUD API for products with search, filtering and ordering."""

    # Serializer used to render and validate product data in API responses/requests
    serializer_class = ProductSerializer
    # Allow public, unauthenticated access to the product API
    permission_classes = (AllowAny,)
    # Use the product's slug (instead of the default pk) as the URL lookup key
    lookup_field = 'slug'
    # Enable full-text search and field ordering via query parameters
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    # Fields the SearchFilter will match against the ?search= query param
    search_fields = ('name', 'description', 'sku', 'tags__name')
    # Fields that clients are allowed to sort by using ?ordering=
    ordering_fields = ('price', 'created_at', 'name', 'avg_rating')
    # Default ordering applied when no explicit ordering is requested
    ordering = ('-created_at',)

    def get_queryset(self):
        # Base queryset: fetch all products with related rows joined to avoid N+1 queries
        queryset = (
            Product.objects.all()
            # select_related: JOIN for one-to-one/foreign keys (category, brand)
            .select_related('category', 'brand')
            # prefetch_related: separate lookups for reverse/many-to-many relations
            .prefetch_related('images', 'tags', 'variants')
            # annotate: attach computed aggregates (average rating, review count) per product
            .annotate(
                avg_rating=Avg('reviews__rating'),
                num_reviews=Count('reviews'),
            )
        )
        # Read all filtering query parameters from the request
        params = self.request.query_params
        category = params.get('category')
        brand = params.get('brand')
        featured = params.get('featured')
        is_new = params.get('is_new')
        best_seller = params.get('best_seller')
        min_price = params.get('min_price')
        max_price = params.get('max_price')
        # Filter by category slug when provided
        if category:
            queryset = queryset.filter(category__slug=category)
        # Filter by brand slug when provided
        if brand:
            queryset = queryset.filter(brand__slug=brand)
        # Only include featured products when the flag is set to "1"/"true"
        if featured in ('1', 'true'):
            queryset = queryset.filter(featured=True)
        # Only include new products when the flag is set to "1"/"true"
        if is_new in ('1', 'true'):
            queryset = queryset.filter(is_new=True)
        # Only include best sellers when the flag is set to "1"/"true"
        if best_seller in ('1', 'true'):
            queryset = queryset.filter(best_seller=True)
        # Filter by minimum price (price greater than or equal)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        # Filter by maximum price (price less than or equal)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        return queryset


def product_list(request):
    """Render the shop page with filtering, sorting and pagination."""
    # Start from active products, joining brand/category to avoid extra queries
    queryset = Product.objects.filter(is_active=True).select_related('brand', 'category')
    # Prefetch images so the template can access them without extra queries
    queryset = queryset.prefetch_related('images')

    # Read filter/sort inputs from GET parameters
    q = request.GET.get('q')
    category = request.GET.get('category')
    brand = request.GET.get('brand')
    sort = request.GET.get('sort', 'newest')

    # Full-text-ish search across name, description and SKU using OR conditions
    if q:
        queryset = queryset.filter(
            Q(name__icontains=q) | Q(description__icontains=q) | Q(sku__icontains=q)
        )
    # Restrict to a single category by its slug
    if category:
        queryset = queryset.filter(category__slug=category)
    # Restrict to a single brand by its slug
    if brand:
        queryset = queryset.filter(brand__slug=brand)

    # Apply the requested sort option to the queryset
    if sort == 'price_asc':
        queryset = queryset.order_by('price')
    elif sort == 'price_desc':
        queryset = queryset.order_by('-price')
    elif sort == 'best':
        queryset = queryset.order_by('-best_seller', '-created_at')
    elif sort == 'rating':
        # Annotate with average rating then sort descending by it
        queryset = queryset.annotate(avg=Avg('reviews__rating')).order_by('-avg')
    else:
        # Default sort: newest products first
        queryset = queryset.order_by('-created_at')

    # Active brands for the sidebar filter UI
    brands = Brand.objects.filter(is_active=True)
    # Top-level (parent-less) active categories for navigation
    categories = request_categories()
    # Paginator: split the queryset into pages of 12 products each
    paginator = Paginator(queryset, 12)
    # Determine which page to show (default to page 1)
    page_number = request.GET.get('page', 1)
    # Return the Page object for the requested page (handles invalid pages safely)
    products = paginator.get_page(page_number)

    # Build the template context with products and current filter/sort state
    context = {
        'products': products,
        'brands': brands,
        'categories': categories,
        'query': q or '',
        'sort': sort,
        'selected_category': category,
        'selected_brand': brand,
        'title': 'Shop',
    }
    # Render the shop/listing template with the assembled context
    return render(request, 'products/list.html', context)


def request_categories():
    # Lazily import Category to avoid a circular import at module load time
    from categories.models import Category
    # Return top-level categories (no parent) that are currently active
    return Category.objects.filter(is_active=True, parent__isnull=True)


def product_detail(request, slug):
    """Render a single product with gallery, variants and reviews."""
    # Fetch the product by slug (404 if missing/inactive) with related data prefetched
    product = get_object_or_404(
        Product.objects.select_related('brand', 'category').prefetch_related(
            'images', 'tags', 'variants', 'variants__attribute_values'
        ),
        slug=slug, is_active=True,
    )
    # Fetch approved reviews for this product, newest first, with the author joined
    reviews = Review.objects.filter(
        product=product, status='approved'
    ).select_related('user').order_by('-created_at')
    # Suggest up to 4 other active products in the same category (excluding this one)
    related = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(pk=product.pk).prefetch_related('images')[:4]

    # Assemble context for the product detail template
    context = {
        'product': product,
        'reviews': reviews,
        'related': related,
        'average_rating': product.average_rating,
        'review_count': product.review_count,
    }
    # Render the product detail page
    return render(request, 'products/detail.html', context)


def home(request):
    """Render the home page with featured / new / best sellers."""
    # Featured products: up to 8 active, flagged featured
    featured = Product.objects.filter(is_active=True, featured=True).prefetch_related('images')[:8]
    # New arrivals: up to 8 active, flagged as new
    new_arrivals = Product.objects.filter(is_active=True, is_new=True).prefetch_related('images')[:8]
    # Best sellers: up to 8 active, flagged as best seller
    best_sellers = Product.objects.filter(is_active=True, best_seller=True).prefetch_related('images')[:8]
    # Top-level active categories for the homepage navigation
    categories = request_categories()
    # Build the homepage context
    context = {
        'featured': featured,
        'new_arrivals': new_arrivals,
        'best_sellers': best_sellers,
        'categories': categories,
    }
    # Render the homepage template
    return render(request, 'products/home.html', context)
