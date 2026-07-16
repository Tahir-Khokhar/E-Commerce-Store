"""Views and API endpoints for payments."""

# Import HttpResponse for creating HTTP responses when needed.
from django.http import HttpResponse

# Import helper functions for object retrieval, redirects, and template rendering.
from django.shortcuts import get_object_or_404, redirect, render

# Import DRF permissions and HTTP status codes.
from rest_framework import permissions, status

# Import APIView for creating class-based API endpoints.
from rest_framework.views import APIView

# Import Response to return API responses.
from rest_framework.response import Response

# Import the Payment model used throughout the payment views.
from payments.models import Payment

# Import payment service functions.
from payments.services import (
    create_payment,
    refund_payment,
)

# Import the Order model used by the payment flow.
from orders.models import Order


# ---------------------------------------------------------------------------
# Web views
# ---------------------------------------------------------------------------

# Render the payment method selection page for an order.
def payment_options(request, order_id):
    """Render payment method selection for an order."""

    # Retrieve the requested order or return a 404 response.
    order = get_object_or_404(Order, pk=order_id)

    # Non-owners may still view if session matches; restrict to owner when auth.
    # Prevent authenticated users from viewing another user's order.
    if request.user.is_authenticated and order.user and order.user != request.user:
        return redirect('order_list')

    # Render the payment options page.
    return render(request, 'payments/options.html', {'order': order})


# Handle a successful payment callback.
def payment_success(request):
    """Handle the gateway success redirect and mark the payment complete."""

    # Retrieve the order ID from the query parameters.
    order_id = request.GET.get('order_id')

    # Retrieve the session or transaction identifier.
    session_id = request.GET.get('session_id') or request.GET.get('token')

    # Retrieve the associated order or return a 404 response.
    order = get_object_or_404(Order, pk=order_id)

    # Continue only if a session identifier was provided.
    if session_id:
        # Retrieve the matching payment record.
        payment = Payment.objects.filter(
            order=order, transaction_id=session_id
        ).first()

        # Continue if the payment exists.
        if payment:
            # For this codebase the supported payment methods are
            # bank/jazzcash/COD. Mark the payment completed for any method.
            # Mark the payment as completed.
            payment.mark_completed(transaction_id=session_id)

    # Render the payment success page.
    return render(request, 'payments/success.html', {'order': order})


# Render the payment cancelled page.
def payment_cancel(request):
    """Render the cancelled-payment page."""

    # Retrieve the order ID from the query parameters.
    order_id = request.GET.get('order_id')

    # Retrieve the associated order if an ID was provided.
    order = get_object_or_404(Order, pk=order_id) if order_id else None

    # Render the cancellation page.
    return render(request, 'payments/cancel.html', {'order': order})


# Process a payment request from the web interface.
def payment_process(request, order_id):
    """Web flow: create a payment and redirect to the gateway or order."""

    # Retrieve the requested order or return a 404 response.
    order = get_object_or_404(Order, pk=order_id)

    # Handle only POST requests.
    if request.method == 'POST':
        # Retrieve the selected payment method from the submitted form.
        method = request.POST.get('method')

        try:
            # Create the payment using the selected method.
            result = create_payment(
                order, method, domain=request.build_absolute_uri('/').rstrip('/')
            )

        # Handle unsupported payment methods.
        except ValueError as exc:
            # Render the payment options page with an error message.
            return render(
                request,
                'payments/options.html',
                {'order': order, 'error': str(exc)},
            )

        # Redirect directly to the order page for Cash on Delivery.
        if result.get('cod'):
            return redirect('order_detail', pk=order.id)

        # Redirect to the payment gateway or the order page.
        return redirect(result.get('redirect_url') or 'order_detail', order.id)

    # Redirect back to the payment options page for non-POST requests.
    return redirect('payment_options', order_id=order.id)


# ---------------------------------------------------------------------------
# API views
# ---------------------------------------------------------------------------

# API endpoint for creating payments.
class PaymentCreateAPIView(APIView):
    """Create a payment and return the gateway redirect information."""

    # Require users to be authenticated.
    permission_classes = (permissions.IsAuthenticated,)

    # Handle POST requests.
    def post(self, request):
        # Retrieve the order ID from the request data.
        order_id = request.data.get('order_id')

        # Retrieve the selected payment method.
        method = request.data.get('method')

        # Validate that the required fields are provided.
        if not order_id or not method:
            return Response(
                {'detail': 'order_id and method are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Retrieve the user's order or return a 404 response.
        order = get_object_or_404(Order, pk=order_id, user=request.user)

        # Check whether the order has already been paid.
        if order.payments.filter(status='completed').exists():
            return Response(
                {'detail': 'Order already paid.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Create the payment.
            result = create_payment(
                order, method, domain=request.build_absolute_uri('/').rstrip('/')
            )

        # Handle unsupported payment methods.
        except ValueError as exc:
            return Response(
                {'detail': str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Retrieve the created payment.
        payment = result['payment']

        # Prepare the API response data.
        data = {
            'payment_id': str(payment.id),
            'method': method,
            'status': payment.status,
            'redirect_url': result.get('redirect_url'),
            'session_id': result.get('session_id'),
            'cod': result.get('cod', False),
        }

        # Return the payment details.
        return Response(data, status=status.HTTP_201_CREATED)


# Stripe webhook removed (now using Bank account + JazzCash + COD).


# API endpoint for processing refunds.
class RefundAPIView(APIView):
    """Refund a completed payment through its gateway."""

    # Require users to be authenticated.
    permission_classes = (permissions.IsAuthenticated,)

    # Handle POST requests.
    def post(self, request):
        # Retrieve the payment ID from the request data.
        payment_id = request.data.get('payment_id')

        # Retrieve the refund amount from the request data.
        amount = request.data.get('amount')

        # Retrieve the payment or return a 404 response.
        payment = get_object_or_404(Payment, pk=payment_id)

        # Ensure the user is authorized to refund this payment.
        if payment.user != request.user and not request.user.is_staff:
            return Response(
                {'detail': 'Forbidden.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            # Convert the refund amount to a float.
            amount = float(amount)

        # Use the full payment amount if the provided value is invalid.
        except (TypeError, ValueError):
            amount = float(payment.amount)

        # Process the refund.
        refund_payment(payment, amount)

        # Return the updated payment status.
        return Response(
            {'detail': 'Refund processed.', 'status': payment.status}
        )
