"""URL patterns for the payments app."""

# Import path to define URL routes for the application.
from django.urls import path

# Import the views that handle payment-related requests.
from payments import views

# Define the URL patterns for the payments app.
urlpatterns = [
    # Route to display the available payment options for an order.
    path('options/<uuid:order_id>/', views.payment_options, name='payment_options'),

    # Route to process the selected payment method for an order.
    path('process/<uuid:order_id>/', views.payment_process, name='payment_process'),

    # Route displayed after a successful payment.
    path('success/', views.payment_success, name='payment_success'),

    # Route displayed when a payment is cancelled.
    path('cancel/', views.payment_cancel, name='payment_cancel'),

    # API.

    # API endpoint to create a new payment.
    path('api/create/', views.PaymentCreateAPIView.as_view(), name='payment_create'),

    # API endpoint to process a payment refund.
    path('api/refund/', views.RefundAPIView.as_view(), name='payment_refund'),
]
