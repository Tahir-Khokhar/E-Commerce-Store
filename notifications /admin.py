"""Admin registration for the notifications app."""

# Import Django's admin module to register and configure models in the admin site.
from django.contrib import admin

# Import the models that will be managed through the Django admin interface.
from notifications.models import Notification, LowStockAlert


# Register the Notification model with a custom admin configuration.
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin configuration for notifications."""

    # Display these fields in the notifications list view.
    list_display = ('user', 'type', 'title', 'read', 'created_at')

    # Add filters in the admin sidebar for notification type and read status.
    list_filter = ('type', 'read')

    # Enable searching by title, message, and the related user's email.
    search_fields = ('title', 'message', 'user__email')

    # Make timestamp fields read-only in the admin form.
    readonly_fields = ('created_at', 'updated_at')


# Register the LowStockAlert model with a custom admin configuration.
@admin.register(LowStockAlert)
class LowStockAlertAdmin(admin.ModelAdmin):
    """Admin configuration for low stock alerts."""

    # Display these fields in the low stock alerts list view.
    list_display = ('product_name', 'sku', 'current_stock', 'resolved', 'created_at')

    # Add a sidebar filter for resolved status.
    list_filter = ('resolved',)

    # Enable searching by product name and SKU.
    search_fields = ('product_name', 'sku')

    # Make timestamp fields read-only in the admin form.
    readonly_fields = ('created_at', 'updated_at')
