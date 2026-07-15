"""Reusable field validators."""
# Import regex support, Django validation errors, and translation utilities.
import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_positive(value):
    """Ensure a numeric value is strictly positive."""

    # Check if the value is zero or negative.
    if value is not None and value <= 0:
        # Raise an error for invalid values.
        raise ValidationError(_('Value must be greater than zero.'))


def validate_non_negative(value):
    """Ensure a numeric value is not negative."""

    # Check if the value is negative.
    if value is not None and value < 0:
        # Raise an error for invalid values.
        raise ValidationError(_('Value must not be negative.'))


def validate_percentage(value):
    """Ensure a value is a valid percentage between 0 and 100."""

    # Check if the value is outside the allowed range.
    if value is not None and not (0 <= value <= 100):
        # Raise an error for invalid percentage values.
        raise ValidationError(_('Percentage must be between 0 and 100.'))


def validate_sku(value):
    """Ensure a SKU contains only allowed characters."""

    # Check if the SKU matches the allowed pattern.
    if value and not re.fullmatch(r'[A-Za-z0-9._-]+', value):
        # Raise an error for invalid SKU format.
        raise ValidationError(
            _('SKU may only contain letters, numbers, dots, dashes and underscores.')
        )


def validate_phone(value):
    """Light validation for international phone numbers."""

    # Check if the phone number matches the required format.
    if value and not re.fullmatch(r'\+?[0-9 ()-]{7,20}', value):
        # Raise an error for invalid phone numbers.
        raise ValidationError(_('Enter a valid phone number.'))
