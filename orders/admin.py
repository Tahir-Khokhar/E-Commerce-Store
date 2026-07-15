# Admin registration for categories.

from django.contrib import admin  # Django admin module.

# Import the Category model.
from categories.models import Category


# Register the Category model in the Django admin.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    # Columns displayed in the category list.
    list_display = ('name', 'parent', 'order', 'is_active')

    # Filters shown in the right sidebar.
    list_filter = ('is_active', 'parent')

    # Fields that can be edited directly from the list page.
    list_editable = ('order', 'is_active')

    # Fields used when searching categories.
    search_fields = ('name', 'slug', 'meta_keywords')

    # Automatically fill the slug field from the name field.
    prepopulated_fields = {'slug': ('name',)}

    # These fields are read-only in the admin panel.
    readonly_fields = ('created_at', 'updated_at')
