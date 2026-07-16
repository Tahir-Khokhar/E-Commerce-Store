"""Admin registration for the wishlist app."""

# Import Django's admin module to register and configure models in the admin site.
from django.contrib import admin

# Import the WishlistItem model to be managed through the admin interface.
from wishlist.models import WishlistItem


# Register the WishlistItem model with a custom admin configuration.
@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    """Admin configuration for wishlist items."""

    # Display these fields in the wishlist items list view.
    list_display = ('user', 'product', 'created_at')

    # Add a sidebar filter based on the creation date.
    list_filter = ('created_at',)

    # Enable searching by user email and product name.
    search_fields = ('user__email', 'product__name')

    # Make timestamp fields read-only in the admin form.
    readonly_fields = ('created_at', 'updated_at')
