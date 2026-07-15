"""Template tags for formatting and presentation helpers."""

from django import template
from django.utils.safestring import mark_safe

from core.utils import money

register = template.Library()


@register.filter
def currency(value):
    """Format a numeric value as currency (USD)."""
    return f'${money(value)}'


@register.filter
def percent(value):
    """Format a numeric value as a percentage."""
    try:
        return f'{float(value)}%'
    except (TypeError, ValueError):
        return '0%'


@register.simple_tag
def star_rating(value):
    """Render a simple star rating (out of 5) as unicode stars."""
    try:
        full = round(float(value))
    except (TypeError, ValueError):
        full = 0
    full = max(0, min(5, full))
    return mark_safe('★' * full + '☆' * (5 - full))


@register.filter
def multiply(value, arg):
    """Multiply two numbers in templates."""
    try:
        return float(value) * float(arg)
    except (TypeError, ValueError):
        return 0
