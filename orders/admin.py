from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_amount', 'paid', 'created_at', 'updated_at']
    list_filter = ['paid', 'created_at']
    search_fields = ['id', 'user__username', 'user__email']
    readonly_fields = ['total_amount']

