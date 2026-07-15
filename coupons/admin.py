"""Admin registration for coupons."""

# Import Django admin tools.
from django.contrib import admin

from coupons.models import Coupon, CouponUsage


# Register the Coupon model in the admin panel.
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """Admin configuration for coupons."""

    # Fields displayed in the coupon list.
    list_display = (
        'code', 'discount_type', 'value', 'min_amount', 'used_count',
        'usage_limit', 'active', 'valid_to',
    )

    # Add filters to the admin list view.
    list_filter = ('discount_type', 'active')

    # Enable searching by these fields.
    search_fields = ('code', 'description')

    # Make fields read-only in the admin form.
    readonly_fields = ('used_count', 'created_at', 'updated_at')


# Register the CouponUsage model in the admin panel.
@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    """Admin configuration for coupon usages."""

    # Fields displayed in the usage list.
    list_display = ('coupon', 'user', 'order', 'created_at')

    # Add filters to the admin list view.
    list_filter = ('coupon',)

    # Enable searching by coupon code and user email.
    search_fields = ('coupon__code', 'user__email')

    # Make timestamp fields read-only.
    readonly_fields = ('created_at', 'updated_at')
