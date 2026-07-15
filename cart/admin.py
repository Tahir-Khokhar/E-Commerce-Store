# Admin registration for the cart app.

from django.contrib import admin  # Django admin module.

# Import cart models.
from cart.models import Cart, CartItem


# Display cart items inside the cart admin page.
class CartItemInline(admin.TabularInline):

    # Model displayed as an inline table.
    model = CartItem

    # Do not show extra empty rows.
    extra = 0

    # Fields displayed in the inline table.
    fields = ('product', 'variant', 'quantity')


# Register the Cart model in the Django admin.
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):

    # Columns displayed in the cart list.
    list_display = ('id', 'user', 'session_key', 'created_at')

    # Filters shown in the right sidebar.
    list_filter = ('created_at',)

    # Fields used for searching carts.
    search_fields = ('user__email', 'session_key')

    # Prevent these fields from being edited.
    readonly_fields = ('created_at', 'updated_at')

    # Show related cart items inside the cart page.
    inlines = (CartItemInline,)


# Register the CartItem model in the Django admin.
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):

    # Columns displayed in the cart item list.
    list_display = ('cart', 'product', 'variant', 'quantity')

    # Fields used for searching cart items.
    search_fields = ('product__name', 'cart__id')
