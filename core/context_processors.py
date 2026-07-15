"""Global template context processors."""

from django.conf import settings

from products.models import Product
from categories.models import Category


def global_context(request):
    """Inject common values (cart count, categories) into templates."""

    # Create the shared template context.
    context = {
        'site_name': 'Ecommerence',

        # Get up to 12 active categories.
        'categories': Category.objects.filter(is_active=True)[:12],
    }

    cart_count = 0

    # Get the user from the request safely.
    user = getattr(request, 'user', None)

    if user and user.is_authenticated:
        # Import lazily to avoid circular imports.
        from cart.models import Cart

        # Get the user's cart.
        cart = Cart.objects.filter(user=user).first()

        if cart:
            # Calculate the total quantity of cart items.
            cart_count = sum(item.quantity for item in cart.items.all())

    # Add the cart count to the context.
    context['cart_count'] = cart_count

    # Return the context dictionary.
    return context
