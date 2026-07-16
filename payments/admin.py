"""Admin registration for the payments app."""

# Import Django's admin module to register and configure models in the admin interface.
from django.contrib import admin

# Import the Payment model to make it manageable through the admin site.
from payments.models import Payment


# Register the Payment model with a custom admin configuration.
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin configuration for payments."""

    # Display these fields in the payments list view.
    list_display = ('order', 'user', 'method', 'amount', 'status', 'created_at')

    # Add sidebar filters for payment method, status, and creation date.
    list_filter = ('method', 'status', 'created_at')

    # Enable searching by order number, transaction ID, and user email.
    search_fields = ('order__order_number', 'transaction_id', 'user__email')

    # Make these fields read-only in the admin form.
    readonly_fields = (
        'created_at',
        'updated_at',
        'gateway_response',
        'refunded_amount',
    )
