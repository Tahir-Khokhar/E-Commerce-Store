# Central API URL configuration using Django REST Framework routers.

from django.urls import path, include  # Used to define and include URL patterns.
from rest_framework.routers import DefaultRouter  # Automatically creates CRUD routes for ViewSets.
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView  # API schema and Swagger documentation.
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView  # JWT authentication endpoints.

# Import authentication and account views.
from accounts.views import (
    RegisterView,
    LoginView,
    LogoutView,
    ProfileView,
    AddressViewSet,
    EmailVerifyView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    DashboardView,
)

# Import application ViewSets.
from categories.views import CategoryViewSet
from products.views import ProductViewSet
from reviews.views import ReviewViewSet, ReviewHelpfulAPIView
from coupons.views import CouponViewSet
from orders.views import (
    OrderViewSet,
    CheckoutAPIView,
    CancelOrderAPIView,
    RefundRequestAPIView,
    AdminRefundViewSet,
)
from cart.views import (
    CartAPIView,
    AddToCartAPIView,
    UpdateCartItemAPIView,
    RemoveCartItemAPIView,
    ApplyCouponAPIView,
    MergeCartAPIView,
)
from wishlist.views import (
    WishlistAPIView,
    WishlistItemAPIView,
    WishlistMoveToCartAPIView,
)
from payments.views import (
    PaymentCreateAPIView,
    RefundAPIView,
)
from notifications.views import NotificationViewSet, MarkAllReadAPIView


# Create a router for ViewSets.
router = DefaultRouter()

# Register product endpoints.
router.register(r'products', ProductViewSet, basename='product')

# Register category endpoints.
router.register(r'categories', CategoryViewSet, basename='category')

# Register review endpoints.
router.register(r'reviews', ReviewViewSet, basename='review')

# Register coupon endpoints.
router.register(r'coupons', CouponViewSet, basename='coupon')

# Register order endpoints.
router.register(r'orders', OrderViewSet, basename='order')

# Register address endpoints.
router.register(r'addresses', AddressViewSet, basename='address')

# Register admin refund endpoints.
router.register(r'admin/refunds', AdminRefundViewSet, basename='admin-refund')

# Register notification endpoints.
router.register(r'notifications', NotificationViewSet, basename='notification')


# List of all API URLs.
urlpatterns = [

    # ---------------- Authentication ----------------

    # Register a new user.
    path('auth/register/', RegisterView.as_view(), name='api-register'),

    # User login.
    # as_view() converts a class-based view into a callable view function.
    path('auth/login/', LoginView.as_view(), name='api-login'),

    # User logout.
    path('auth/logout/', LogoutView.as_view(), name='api-logout'),

    # Refresh an expired JWT access token.
    path('auth/refresh/', TokenRefreshView.as_view(), name='api-token-refresh'),

    # Verify whether a JWT token is valid.
    path('auth/verify/', TokenVerifyView.as_view(), name='api-token-verify'),

    # Verify user email.
    path('auth/verify-email/', EmailVerifyView.as_view(), name='api-verify-email'),

    # Request a password reset.
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='api-password-reset'),

    # Confirm password reset.
    path('auth/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='api-password-reset-confirm'),

    # Get or update the logged-in user's profile.
    path('auth/me/', ProfileView.as_view(), name='api-profile'),

    # User dashboard data.
    path('auth/dashboard/', DashboardView.as_view(), name='api-dashboard'),

    # ---------------- Cart ----------------

    # View current cart.
    path('cart/', CartAPIView.as_view(), name='api-cart'),

    # Add an item to the cart.
    path('cart/add/', AddToCartAPIView.as_view(), name='api-cart-add'),

    # Update a cart item.
    # <uuid:item_id> captures a UUID and passes it as item_id.
    path('cart/items/<uuid:item_id>/', UpdateCartItemAPIView.as_view(), name='api-cart-update'),

    # Remove an item from the cart.
    path('cart/items/<uuid:item_id>/remove/', RemoveCartItemAPIView.as_view(), name='api-cart-remove'),

    # Apply a coupon code.
    path('cart/coupon/', ApplyCouponAPIView.as_view(), name='api-cart-coupon'),

    # Merge guest cart into user cart.
    path('cart/merge/', MergeCartAPIView.as_view(), name='api-cart-merge'),

    # ---------------- Wishlist ----------------

    # View wishlist.
    path('wishlist/', WishlistAPIView.as_view(), name='api-wishlist'),

    # Manage a specific wishlist item.
    path('wishlist/<uuid:pk>/', WishlistItemAPIView.as_view(), name='api-wishlist-item'),

    # Move a wishlist item to the cart.
    path('wishlist/<uuid:pk>/move/', WishlistMoveToCartAPIView.as_view(), name='api-wishlist-move'),

    # ---------------- Reviews ----------------

    # Mark a review as helpful.
    path('reviews/<uuid:pk>/helpful/', ReviewHelpfulAPIView.as_view(), name='api-review-helpful'),

    # ---------------- Orders ----------------

    # Checkout and create an order.
    path('checkout/', CheckoutAPIView.as_view(), name='api-checkout'),

    # Cancel an existing order.
    path('orders/<uuid:pk>/cancel/', CancelOrderAPIView.as_view(), name='api-order-cancel'),

    # Request an order refund.
    path('orders/<uuid:pk>/refund/', RefundRequestAPIView.as_view(), name='api-order-refund'),

    # ---------------- Payments ----------------

    # Create a payment.
    path('payments/create/', PaymentCreateAPIView.as_view(), name='api-payment-create'),

    # Process a payment refund.
    path('payments/refund/', RefundAPIView.as_view(), name='api-payment-refund'),

    # ---------------- API Documentation ----------------

    # Generate the OpenAPI schema.
    path('schema/', SpectacularAPIView.as_view(), name='schema'),

    # Display the Swagger UI.
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # ---------------- Router URLs ----------------

    # include() adds all URLs automatically generated by the router.
    path('', include(router.urls)),
]
