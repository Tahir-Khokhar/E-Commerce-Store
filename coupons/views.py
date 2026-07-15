"""Views and API endpoints for coupons."""

# Import DRF viewset classes.
from rest_framework import viewsets

# Import permission class for admin-only access.
from rest_framework.permissions import IsAdminUser

from coupons.models import Coupon
from coupons.serializers import CouponSerializer


class CouponViewSet(viewsets.ModelViewSet):
    """CRUD API for coupons (admin only)."""

    # Get all coupon records from the database.
    queryset = Coupon.objects.all()

    # Use CouponSerializer for converting data.
    serializer_class = CouponSerializer

    # Allow access only to admin users.
    permission_classes = (IsAdminUser,)

    # Use coupon code instead of ID for lookup.
    lookup_field = 'code'
