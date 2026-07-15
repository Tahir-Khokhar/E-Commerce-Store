"""Generic helper utilities."""

import random
import string

from django.utils.text import slugify as django_slugify


def generate_unique_slug(model, title, slug_field='slug'):
    """Create a unique slug for ``model`` based on ``title``."""

    # Convert the title into a URL-friendly slug.
    base = django_slugify(title) or 'item'

    # Set the initial slug value.
    slug = base

    # Start the counter for duplicate slugs.
    n = 1

    # Get all records from the model.
    queryset = model._default_manager.all()

    # Check and update slug until it becomes unique.
    while queryset.filter(**{slug_field: slug}).exists():
        slug = f'{base}-{n}'
        n += 1

    # Return the unique slug.
    return slug


def generate_coupon_code(length=8):
    """Generate a random uppercase coupon code."""

    # Create characters for the coupon code.
    alphabet = string.ascii_uppercase + string.digits

    # Generate a random code of given length.
    return ''.join(random.choices(alphabet, k=length))


def generate_tracking_number():
    """Generate a human readable order tracking number."""

    # Generate a tracking number with random digits.
    return 'TRK' + ''.join(random.choices(string.digits, k=10))


def money(value):
    """Format a decimal value as a currency string."""

    try:
        # Convert value to float and format as currency.
        return f'{float(value):,.2f}'

    # Return default value for invalid input.
    except (TypeError, ValueError):
        return '0.00'
