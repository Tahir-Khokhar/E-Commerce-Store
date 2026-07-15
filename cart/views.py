# Views and API endpoints for the cart.

# Django shortcut functions.
from django.shortcuts import get_object_or_404, redirect, render

# DRF classes and helpers.
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

# Import cart models.
from cart.models import Cart, CartItem

# Import cart serializers.
from cart.serializers import (
    CartItemCreateSerializer,
    CartItemSerializer,
    CartSerializer,
)

# Import helper function for merging guest carts.
from cart.utils import merge_guest_cart

# Import product models.
from products.models import Product, ProductVariant

# Import coupon model and validation helper.
from coupons.models import Coupon
from coupons.services import validate_coupon


# Return the current user's cart or the guest cart.
def get_request_cart(request):

    # If the user is logged in, return their cart.
    if request.user.is_authenticated:
        return Cart.get_or_create_cart(user=request.user)

    # Create a session for guest users if one doesn't exist.
    if not request.session.session_key:

        # save() creates a new session.
        request.session.save()

    # Return the guest cart using the session key.
    return Cart.get_or_create_cart(session_key=request.session.session_key)


# ---------------------------------------------------------------------------
# API views
# ---------------------------------------------------------------------------

# API for viewing the current cart.
class CartAPIView(APIView):

    # Anyone can access this endpoint.
    permission_classes = (permissions.AllowAny,)

    # Handle GET requests.
    def get(self, request):

        # Get the current cart.
        cart = get_request_cart(request)

        # Return serialized cart data.
        return Response(CartSerializer(cart).data)


# API for adding items to the cart.
class AddToCartAPIView(APIView):

    # Allow guest users.
    permission_classes = (permissions.AllowAny,)

    # Handle POST requests.
    def post(self, request):

        # Validate incoming data.
        serializer = CartItemCreateSerializer(data=request.data)

        # Raise an error automatically if validation fails.
        serializer.is_valid(raise_exception=True)

        # Get the user's cart.
        cart = get_request_cart(request)

        # Find the product or return a 404 error.
        product = get_object_or_404(
            Product,
            pk=serializer.validated_data['product_id']
        )

        # Default to no variant.
        variant = None

        # Get the optional variant ID.
        variant_id = serializer.validated_data.get('variant_id')

        # Load the variant if one was provided.
        if variant_id:
            variant = get_object_or_404(
                Product,
                pk=variant_id,
                product=product
            )

        # Add the item to the cart.
        cart.add_item(
            product,
            serializer.validated_data['quantity'],
            variant
        )

        # Return the updated cart.
        return Response(
            CartSerializer(cart).data,
            status=status.HTTP_200_OK
        )


# API for updating a cart item.
class UpdateCartItemAPIView(APIView):

    permission_classes = (permissions.AllowAny,)

    # Handle PATCH requests.
    def patch(self, request, item_id):

        # Get the current cart.
        cart = get_request_cart(request)

        # Find the cart item or return 404.
        item = get_object_or_404(
            CartItem,
            pk=item_id,
            cart=cart
        )

        # Get the new quantity.
        quantity = request.data.get('quantity')

        # Continue only if quantity was provided.
        if quantity is not None:

            # Remove the item if quantity is zero or less.
            if int(quantity) <= 0:
                item.delete()

            else:
                # Update the quantity.
                item.quantity = int(quantity)

                # Save changes to the database.
                item.save()

        # Return the updated cart.
        return Response(CartSerializer(cart).data)


# API for removing a cart item.
class RemoveCartItemAPIView(APIView):

    permission_classes = (permissions.AllowAny,)

    # Handle DELETE requests.
    def delete(self, request, item_id):

        # Get the current cart.
        cart = get_request_cart(request)

        # Find the cart item.
        item = get_object_or_404(
            CartItem,
            pk=item_id,
            cart=cart
        )

        # Delete the item.
        item.delete()

        # Return the updated cart.
        return Response(
            CartSerializer(cart).data,
            status=status.HTTP_200_OK
        )


# API for applying a coupon.
class ApplyCouponAPIView(APIView):

    permission_classes = (permissions.AllowAny,)

    # Handle POST requests.
    def post(self, request):

        # Get the current cart.
        cart = get_request_cart(request)

        # Read the coupon code.
        # get() returns '' if the key doesn't exist.
        code = request.data.get('code', '')

        try:

            # Find an active coupon.
            coupon = Coupon.objects.get(
                code__iexact=code,
                is_active=True
            )

        except Coupon.DoesNotExist:

            # Return an error if the coupon doesn't exist.
            return Response(
                {'detail': 'Invalid coupon code.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate the coupon.
        error = validate_coupon(
            coupon,
            cart.subtotal,
            request.user
        )

        # Return validation error if any.
        if error:
            return Response(
                {'detail': error},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Save the coupon on the cart.
        cart.coupon = coupon
        cart.save()

        # Return the updated cart.
        return Response(CartSerializer(cart).data)


# API for merging a guest cart after login.
class MergeCartAPIView(APIView):

    # Login is required.
    permission_classes = (permissions.IsAuthenticated,)

    # Handle POST requests.
    def post(self, request):

        # Use the provided session key or the current session.
        session_key = (
            request.data.get('session_key')
            or request.session.session_key
        )

        # Merge the guest cart.
        merge_guest_cart(
            request.user,
            session_key
        )

        # Get the user's updated cart.
        cart = Cart.get_or_create_cart(user=request.user)

        # Return the updated cart.
        return Response(CartSerializer(cart).data)
    
# ---------------------------------------------------------------------------
# Web views
# ---------------------------------------------------------------------------

# Display the shopping cart page.
def cart_detail(request):

    # Check if the user is logged in.
    if request.user.is_authenticated:

        # Get the current session key.
        session_key = request.session.session_key

        # Merge the guest cart after login.
        if session_key:
            merge_guest_cart(request.user, session_key)

        # Get the logged-in user's cart.
        cart = Cart.get_or_create_cart(user=request.user)

    else:

        # Create a session for guest users if one doesn't exist.
        if not request.session.session_key:

            # save() creates a new session.
            request.session.save()

        # Get the guest cart.
        cart = Cart.get_or_create_cart(
            session_key=request.session.session_key
        )

    # Default value if no coupon error occurs.
    coupon_error = None

    # Check if the user submitted the coupon form.
    if request.method == 'POST' and 'apply_coupon' in request.POST:

        # Get the coupon code.
        # get() returns an empty string if the key is missing.
        code = request.POST.get('code', '')

        try:

            # Find an active coupon.
            coupon = Coupon.objects.get(
                code__iexact=code,
                is_active=True
            )

            # Validate the coupon.
            error = validate_coupon(
                coupon,
                cart.subtotal,
                request.user
            )

            # Store the error message if validation fails.
            if error:
                coupon_error = error

            else:

                # Apply the coupon.
                cart.coupon = coupon
                cart.save()

        except Coupon.DoesNotExist:

            # Coupon was not found.
            coupon_error = 'Invalid coupon code.'

    # render() combines the template with data and returns an HTML page.
    return render(
        request,
        'cart/cart.html',
        {
            'cart': cart,
            'coupon_error': coupon_error,
        },
    )


# Add a product to the cart.
def add_to_cart(request, slug):

    # Find the product or return a 404 page.
    product = get_object_or_404(
        Product,
        slug=slug,
        is_active=True
    )

    # Read the quantity from the submitted form.
    # int() converts the value to an integer.
    quantity = int(request.POST.get('quantity', 1))

    # Get the selected variant if provided.
    variant_id = request.POST.get('variant')

    # Default to no variant.
    variant = None

    # Find the selected product variant.
    if variant_id:
        variant = get_object_or_404(
            ProductVariant,
            pk=variant_id,
            product=product
        )

    # Get the user's current cart.
    cart = get_request_cart(request)

    # Add the product to the cart.
    cart.add_item(
        product,
        quantity,
        variant
    )

    # redirect() sends the user to another page.
    return redirect('cart_detail')


# Update a cart item's quantity.
def update_cart_item(request, item_id):

    # Get the current cart.
    cart = get_request_cart(request)

    # Find the cart item.
    item = get_object_or_404(
        CartItem,
        pk=item_id,
        cart=cart
    )

    # Only process POST requests.
    if request.method == 'POST':

        # Read the new quantity.
        qty = int(
            request.POST.get(
                'quantity',
                item.quantity
            )
        )

        # Remove the item if the quantity is zero or less.
        if qty <= 0:
            item.delete()

        else:

            # Update the quantity.
            item.quantity = qty

            # Save the changes.
            item.save()

    # Return to the cart page.
    return redirect('cart_detail')


# Remove a cart item.
def remove_cart_item(request, item_id):

    # Get the current cart.
    cart = get_request_cart(request)

    # Find the cart item.
    item = get_object_or_404(
        CartItem,
        pk=item_id,
        cart=cart
    )

    # Delete the item.
    item.delete()

    # Return to the cart page.
    return redirect('cart_detail')
