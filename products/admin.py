"""Admin registrations for the products app."""

# Import Django's admin module to register and configure models in the admin site.
from django.contrib import admin

# Import all product-related models that will be managed through the admin interface.
from products.models import (
    Attribute,
    AttributeValue,
    Brand,
    Product,
    ProductImage,
    ProductVariant,
    Tag,
)


# Inline editor for managing product images from the product admin page.
class ProductImageInline(admin.TabularInline):
    """Inline editor for product gallery images."""

    # Specify the related model displayed inline.
    model = ProductImage

    # Display one extra empty form for adding new images.
    extra = 1

    # Display only these fields in the inline form.
    fields = ('image', 'alt', 'is_primary', 'order')


# Inline editor for managing product variants from the product admin page.
class ProductVariantInline(admin.TabularInline):
    """Inline editor for product variants."""

    # Specify the related model displayed inline.
    model = ProductVariant

    # Do not display any extra empty forms by default.
    extra = 0

    # Display only these fields in the inline form.
    fields = ('name', 'sku', 'price', 'stock', 'track_inventory')


# Register the Product model with a custom admin configuration.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for products."""

    # Display these fields in the product list view.
    list_display = (
        'name', 'sku', 'category', 'brand', 'price', 'stock',
        'featured', 'is_new', 'best_seller', 'is_active',
    )

    # Add sidebar filters for commonly filtered product fields.
    list_filter = (
        'is_active', 'featured', 'is_new', 'best_seller', 'category', 'brand'
    )

    # Enable searching by product name, SKU, barcode, and description.
    search_fields = ('name', 'sku', 'barcode', 'description')

    # Automatically populate the slug field from the product name.
    prepopulated_fields = {'slug': ('name',)}

    # Make timestamp fields read-only in the admin form.
    readonly_fields = ('created_at', 'updated_at')

    # Display related images and variants as inline editors.
    inlines = (ProductImageInline, ProductVariantInline)

    # Allow these fields to be edited directly from the list view.
    list_editable = ('featured', 'is_new', 'best_seller', 'is_active')

    # Register custom bulk actions.
    actions = ['mark_featured', 'mark_inactive']

    # Register this method as an admin action with a custom description.
    @admin.action(description='Mark selected products as featured')
    def mark_featured(self, request, queryset):
        # Update all selected products to featured.
        queryset.update(featured=True)

    # Register this method as an admin action with a custom description.
    @admin.action(description='Mark selected products as inactive')
    def mark_inactive(self, request, queryset):
        # Update all selected products to inactive.
        queryset.update(is_active=False)


# Register the Brand model with a custom admin configuration.
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Admin configuration for brands."""

    # Display these fields in the brand list view.
    list_display = ('name', 'website', 'is_active')

    # Enable searching by brand name.
    search_fields = ('name',)

    # Automatically populate the slug field from the brand name.
    prepopulated_fields = {'slug': ('name',)}


# Register the Tag model with a custom admin configuration.
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin configuration for tags."""

    # Display these fields in the tag list view.
    list_display = ('name', 'is_active')

    # Enable searching by tag name.
    search_fields = ('name',)

    # Automatically populate the slug field from the tag name.
    prepopulated_fields = {'slug': ('name',)}


# Register the Attribute model with a custom admin configuration.
@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    """Admin configuration for attributes."""

    # Display these fields in the attribute list view.
    list_display = ('name', 'is_active')

    # Enable searching by attribute name.
    search_fields = ('name',)

    # Automatically populate the slug field from the attribute name.
    prepopulated_fields = {'slug': ('name',)}


# Register the AttributeValue model with a custom admin configuration.
@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    """Admin configuration for attribute values."""

    # Display these fields in the attribute value list view.
    list_display = ('attribute', 'value')

    # Enable searching by value and related attribute name.
    search_fields = ('value', 'attribute__name')


# Register the ProductImage model with a custom admin configuration.
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Admin configuration for product images."""

    # Display these fields in the product image list view.
    list_display = ('product', 'is_primary', 'order')

    # Add a sidebar filter for the primary image flag.
    list_filter = ('is_primary',)


# Register the ProductVariant model with a custom admin configuration.
@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """Admin configuration for product variants."""

    # Display these fields in the product variant list view.
    list_display = ('product', 'name', 'sku', 'stock', 'is_active')

    # Enable searching by SKU and variant name.
    search_fields = ('sku', 'name')
