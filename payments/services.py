"""Payment gateway integrations: Stripe, PayPal and Cash on Delivery."""

# Import json to serialize gateway response data for storage.
import json

# Import urllib.request to make HTTP requests when needed.
import urllib.request

# Import urllib.parse to encode and manipulate URL data.
import urllib.parse

# Import base64 to encode and decode binary data when required.
import base64

# Import Django settings to access application configuration values.
from django.conf import settings

# Import the Payment model used to create and update payment records.
from payments.models import Payment

# Import payment method constants used throughout the payment flow.
from core.constants import (
    PAYMENT_METHOD_BANK,
    PAYMENT_METHOD_JAZZCASH,
    PAYMENT_METHOD_COD,
)

# Import the Stripe library for Stripe payment integrations.
import stripe as stripe_lib


# ---------------------------------------------------------------------------
# Unified interface
# ---------------------------------------------------------------------------


# Create a payment record and initialize the selected payment method.
def create_payment(order, method, domain=''):
    """Create a payment record and initiate the chosen payment method flow.

    This project now supports:
    - Bank account (manual transfer)
    - JazzCash (manual / mock flow)
    - COD

    Redirect URLs are not required for these methods; the user stays on site.
    """

    # Create and save a new payment record.
    payment = Payment.objects.create(
        order=order,
        user=order.user,
        method=method,
        amount=order.total,
        currency='USD',
        status='pending',
    )

    # Prepare the default response structure.
    result = {'payment': payment, 'redirect_url': None}

    # Handle Cash on Delivery payments.
    if method == PAYMENT_METHOD_COD:
        # Keep the payment in a pending state.
        payment.status = 'pending'

        # Save the updated payment.
        payment.save()

        # Indicate that this is a Cash on Delivery payment.
        result['cod'] = True

        # Return the payment result.
        return result

    # Handle manual bank transfer payments.
    if method == PAYMENT_METHOD_BANK:
        # In a real integration, you would show bank details + mark completed on admin confirmation.

        # Store gateway-related information for the payment.
        payment.gateway_response = json.dumps({'type': 'bank_account'})

        # Save the updated payment.
        payment.save()

        # Return the configured bank account details.
        result['bank_details'] = {
            'account_name': getattr(settings, 'BANK_ACCOUNT_NAME', 'Ecommerence'),
            'iban': getattr(settings, 'BANK_ACCOUNT_IBAN', '—'),
            'bank_name': getattr(settings, 'BANK_NAME', '—'),
        }

        # Return the payment result.
        return result

    # Handle JazzCash payments.
    if method == PAYMENT_METHOD_JAZZCASH:
        # In a real integration, you would initiate a JazzCash payment request and verify callbacks.

        # Store gateway-related information for the payment.
        payment.gateway_response = json.dumps({'type': 'jazzcash'})

        # Save the updated payment.
        payment.save()

        # Return the configured JazzCash merchant details.
        result['jazzcash_details'] = {
            'merchant_phone': getattr(settings, 'JAZZCASH_MERCHANT_PHONE', '—'),
        }

        # Return the payment result.
        return result

    # Raise an error if the payment method is not supported.
    raise ValueError('Unsupported payment method.')


# Process a refund for an existing payment.
def refund_payment(payment, amount):
    """Refund a payment.

    For bank/JazzCash methods we record the refund locally.
    """

    # Apply the refund to the payment record.
    payment.apply_refund(amount)

    # Update the related order if it has not already been marked as refunded.
    if payment.order.status != 'refunded':
        payment.order.set_status('refunded', note=f'Refunded {amount}')

    # Return the updated payment object.
    return payment
