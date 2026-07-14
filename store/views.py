from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Category, Size, Color, Variant


def home(request):
    """Homepage - category dashboard with featured products"""
    available_products = Product.objects.filter(available=True).select_related('category').order_by('-created_at')
    categories = Category.objects.all().order_by('name')

    # Group products by category for dashboard rendering.
    # Only include categories that actually have available products.
    category_products = []
    for category in categories:
        products_in_category = [p for p in available_products if p.category_id == category.id]
        if products_in_category:
            category_products.append({
                'category': category,
                'products': products_in_category,
            })

    return render(request, 'store/home.html', {
        'category_products': category_products,
    })



def product_detail(request, slug):
    """Product detail page"""
    product = get_object_or_404(Product, slug=slug, available=True)

    # Variant selection UI needs available Sizes + Colors.
    # For now, variants are global (we use Variant table size/color combinations).
    # Product-level variant inventory is not implemented in your models yet.
    product_sizes = Size.objects.all()
    product_colors = Color.objects.all()

    return render(
        request,
        'store/product_details.html',
        {
            'product': product,
            'product_sizes': product_sizes,
            'product_colors': product_colors,
        },
    )



def product_list(request, category_slug=None):
    """List products with search, category, and price range filters"""
    products = Product.objects.filter(available=True)

    category = None
    query = request.GET.get('q', '')

    # Search
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )

    # Category Filter
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # Price Filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(base_price__gte=min_price)
    if max_price:
        products = products.filter(base_price__lte=max_price)

    categories = Category.objects.all()

    return render(request, 'store/product_list.html', {
        'products': products,
        'category': category,
        'categories': categories,
        'query': query
    })
