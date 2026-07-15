# Cart calculation utilities: tax, shipping, discounts, and totals.

from decimal import Decimal  # Provides accurate decimal calculations for money.

from django.conf import settings  # Access project settings.


# Calculate the final cart totals.
def calculate_totals(subtotal, coupon=None, shipping_address=None):
    # Calculate discount, tax, shipping, and final total.

    # Convert subtotal to a Decimal to avoid floating-point errors.
    subtotal = Decimal(str(subtotal))

    # Default discount is zero.
    discount = Decimal('0.00')

    # Apply coupon discount if one is provided.
    if coupon is not None:
        discount = coupon.calculate_discount(subtotal)

    # Prevent the subtotal from becoming negative.
    # max() returns the larger of the two values.
    discounted = max(subtotal - discount, Decimal('0.00'))

    # Get the tax rate from settings.
    # getattr() returns the setting value or the default if it doesn't exist.
    tax_rate = Decimal(str(getattr(settings, 'DEFAULT_TAX_RATE', 0)))

    # Calculate tax and round to two decimal places.
    # quantize() rounds a Decimal to the specified precision.
    tax = (discounted * tax_rate).quantize(Decimal('0.01'))

    # Get the default shipping cost.
    shipping = Decimal(
        str(getattr(settings, 'DEFAULT_SHIPPING_FLAT_RATE', 0))
    )

    # Get the free shipping threshold.
    free_threshold = Decimal(
        str(getattr(settings, 'FREE_SHIPPING_THRESHOLD', 0))
    )

    # Apply free shipping if the discounted subtotal reaches the threshold.
    if free_threshold > 0 and discounted >= free_threshold:
        shipping = Decimal('0.00')

    # Do not charge shipping for an empty cart.
    if discounted <= 0:
        shipping = Decimal('0.00')

    # Calculate the final total.
    total = discounted + tax + shipping

    # Return all calculated values.
    return {
        'subtotal': subtotal.quantize(Decimal('0.01')),
        'discount': discount.quantize(Decimal('0.01')),
        'tax': tax,
        'shipping': shipping,
        'total': total.quantize(Decimal('0.01')),
    }


# Merge a guest cart into a logged-in user's cart.
def merge_guest_cart(user, session_key):

    # Import models here to avoid circular imports.
    from cart.models import Cart, CartItem

    # first() returns the first matching cart or None.
    guest_cart = Cart.objects.filter(session_key=session_key).first()

    # Stop if no guest cart exists.
    if not guest_cart:
        return None

    # Get or create the user's cart.
    # get_or_create() returns (object, created).
    user_cart, _ = Cart.objects.get_or_create(user=user)

    # Move each guest cart item.
    for item in guest_cart.cart_items.all():

        # Look for the same product and variant in the user's cart.
        existing = CartItem.objects.filter(
            cart=user_cart,
            product=item.product,
            variant=item.variant,
        ).first()

        # If the item already exists, increase its quantity.
        if existing:
            existing.quantity += item.quantity
            existing.save()

        # Otherwise move the item into the user's cart.
        else:
            item.cart = user_cart
            item.save()

    # Delete the guest cart after merging.
    guest_cart.delete()

    # Return the updated user cart.
    return user_cart
