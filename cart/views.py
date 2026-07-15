"""Views and API endpoints for the cart."""

from django.shortcuts import get_object_or_404, redirect, render

from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Cart, CartItem
from cart.serializers import (
    CartItemCreateSerializer,
    CartItemSerializer,
    CartSerializer,
)
from cart.utils import merge_guest_cart
from products.models import Product, ProductVariant
from coupons.models import Coupon
from coupons.services import validate_coupon


def get_request_cart(request):
    """Return the active cart for the request (user or session)."""
    if request.user.is_authenticated:
        return Cart.get_or_create_cart(user=request.user)
    # Ensure a session key exists for guest carts.
    if not request.session.session_key:
        request.session.save()
    return Cart.get_or_create_cart(session_key=request.session.session_key)


# ---------------------------------------------------------------------------
# API views
# ---------------------------------------------------------------------------

class CartAPIView(APIView):
    """Retrieve the current cart for the request."""

    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        cart = get_request_cart(request)
        return Response(CartSerializer(cart).data)


class AddToCartAPIView(APIView):
    """Add a product (optionally a variant) to the cart."""

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = CartItemCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = get_request_cart(request)
        product = get_object_or_404(Product, pk=serializer.validated_data['product_id'])
        variant = None
        variant_id = serializer.validated_data.get('variant_id')
        if variant_id:
            variant = get_object_or_404(ProductVariant, pk=variant_id, product=product)
        cart.add_item(product, serializer.validated_data['quantity'], variant)
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


class UpdateCartItemAPIView(APIView):
    """Update the quantity of a cart item."""

    permission_classes = (permissions.AllowAny,)

    def patch(self, request, item_id):
        cart = get_request_cart(request)
        item = get_object_or_404(CartItem, pk=item_id, cart=cart)
        quantity = request.data.get('quantity')
        if quantity is not None:
            if int(quantity) <= 0:
                item.delete()
            else:
                item.quantity = int(quantity)
                item.save()
        return Response(CartSerializer(cart).data)


class RemoveCartItemAPIView(APIView):
    """Remove a cart item."""

    permission_classes = (permissions.AllowAny,)

    def delete(self, request, item_id):
        cart = get_request_cart(request)
        item = get_object_or_404(CartItem, pk=item_id, cart=cart)
        item.delete()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


class ApplyCouponAPIView(APIView):
    """Apply a coupon code to the cart."""

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        cart = get_request_cart(request)
        code = request.data.get('code', '')
        try:
            coupon = Coupon.objects.get(code__iexact=code, is_active=True)
        except Coupon.DoesNotExist:
            return Response({'detail': 'Invalid coupon code.'}, status=status.HTTP_400_BAD_REQUEST)
        error = validate_coupon(coupon, cart.subtotal, request.user)
        if error:
            return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)
        cart.coupon = coupon
        cart.save()
        return Response(CartSerializer(cart).data)


class MergeCartAPIView(APIView):
    """Merge a guest cart into the authenticated user's cart."""

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        session_key = request.data.get('session_key') or request.session.session_key
        merge_guest_cart(request.user, session_key)
        cart = Cart.get_or_create_cart(user=request.user)
        return Response(CartSerializer(cart).data)


# ---------------------------------------------------------------------------
# Web views
# ---------------------------------------------------------------------------

def cart_detail(request):
    """Render the cart page and merge a guest cart on login."""
    if request.user.is_authenticated:
        session_key = request.session.session_key
        if session_key:
            merge_guest_cart(request.user, session_key)
        cart = Cart.get_or_create_cart(user=request.user)
    else:
        if not request.session.session_key:
            request.session.save()
        cart = Cart.get_or_create_cart(session_key=request.session.session_key)

    coupon_error = None
    if request.method == 'POST' and 'apply_coupon' in request.POST:
        code = request.POST.get('code', '')
        try:
            coupon = Coupon.objects.get(code__iexact=code, is_active=True)
            error = validate_coupon(coupon, cart.subtotal, request.user)
            if error:
                coupon_error = error
            else:
                cart.coupon = coupon
                cart.save()
        except Coupon.DoesNotExist:
            coupon_error = 'Invalid coupon code.'

    return render(request, 'cart/cart.html', {'cart': cart, 'coupon_error': coupon_error})


def add_to_cart(request, slug):
    """Add a product to the cart from a form submission."""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    quantity = int(request.POST.get('quantity', 1))
    variant_id = request.POST.get('variant')
    variant = None
    if variant_id:
        variant = get_object_or_404(ProductVariant, pk=variant_id, product=product)
    cart = get_request_cart(request)
    cart.add_item(product, quantity, variant)
    return redirect('cart_detail')


def update_cart_item(request, item_id):
    """Update a cart item quantity from a form submission."""
    cart = get_request_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    if request.method == 'POST':
        qty = int(request.POST.get('quantity', item.quantity))
        if qty <= 0:
            item.delete()
        else:
            item.quantity = qty
            item.save()
    return redirect('cart_detail')


def remove_cart_item(request, item_id):
    """Remove a cart item from a form submission."""
    cart = get_request_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    item.delete()
    return redirect('cart_detail')
