"""Product stock management utilities."""

# Import Decimal for precise decimal arithmetic when needed.
from decimal import Decimal

# Import product-related models used for inventory management.
from products.models import InventoryTransaction, Product, ProductVariant


# Adjust the stock level for a product or variant and record the change.
def adjust_stock(product, quantity_change, transaction_type='adjustment',
                 variant=None, note=''):
    """Adjust stock for a product/variant and log the transaction.

    ``quantity_change`` is negative to decrease stock (e.g. a sale).
    Triggers a low-stock notification when stock falls below threshold.
    """

    # Update stock for a specific product variant if provided.
    if variant is not None:
        # Ensure the stock value never becomes negative.
        variant.stock = max(variant.stock + quantity_change, 0)

        # Save only the updated stock field.
        variant.save(update_fields=['stock'])

        # Store the updated stock value.
        current_stock = variant.stock

    # Otherwise, update the main product stock.
    else:
        # Ensure the stock value never becomes negative.
        product.stock = max(product.stock + quantity_change, 0)

        # Save only the updated stock field.
        product.save(update_fields=['stock'])

        # Store the updated stock value.
        current_stock = product.stock

    # Create an inventory transaction record for auditing purposes.
    InventoryTransaction.objects.create(
        product=product,
        variant=variant,
        transaction_type=transaction_type,
        quantity_change=quantity_change,
        note=note,
    )

    # Check whether the updated stock has reached the low-stock threshold.
    check_low_stock(product, variant, current_stock)

    # Return the updated stock quantity.
    return current_stock


# Check whether a low-stock notification should be sent.
def check_low_stock(product, variant, current_stock):
    """Send a low-stock notification when stock is below the threshold."""

    # Import application settings to access the configured stock threshold.
    from django.conf import settings

    # Retrieve the configured low-stock threshold or use the default value.
    threshold = getattr(settings, 'LOW_STOCK_THRESHOLD', 5)

    # Continue only if the stock is at or below the threshold.
    if current_stock <= threshold:
        try:
            # Import the notification service only when needed to avoid unnecessary imports.
            from notifications.services import notify_low_stock

            # Send a low-stock notification.
            notify_low_stock(product, variant, current_stock)

        # Ignore notification errors so stock updates still succeed.
        except Exception:
            pass
