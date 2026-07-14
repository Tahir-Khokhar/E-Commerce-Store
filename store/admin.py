from django.contrib import admin

from .models import (
    Category,
    Color,
    Product,
    ProductImage,
    Size,
    Subcategory,
    Variant,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'meta_title']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'slug']


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'slug', 'category__name']


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['label']
    search_fields = ['label']


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'hex_code']
    search_fields = ['name']


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ['id', 'size', 'color', 'sku']
    search_fields = ['sku', 'size__label', 'color__name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'subcategory', 'base_price', 'discount_percent', 'available']
    list_filter = ['available', 'category']
    list_editable = ['base_price', 'discount_percent', 'available']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'slug']


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'sort_order']
    search_fields = ['product__name']

