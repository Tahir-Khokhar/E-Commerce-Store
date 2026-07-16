"""Notification services: database + email notifications."""

# Import Django settings to access application configuration values.
from django.conf import settings

# Import send_mail to send emails using the configured email backend.
from django.core.mail import send_mail

# Import render_to_string to render email templates into HTML.
from django.template.loader import render_to_string

# Import strip_tags to create a plain text version of the HTML email.
from django.utils.html import strip_tags

# Import notification-related models used by these services.
from notifications.models import Notification, LowStockAlert

# Import notification type constants used when creating notifications.
from core.constants import (
    NOTIFICATION_ORDER,
    NOTIFICATION_PAYMENT,
    NOTIFICATION_LOW_STOCK,
)


# Create and store a database notification.
def _notify(user, ntype, title, message, link=''):
    """Create a database notification (optionally broadcast)."""

    # Create and save a new notification record.
    return Notification.objects.create(
        user=user, type=ntype, title=title, message=message, link=link
    )


# Render and send an email notification.
def _email(recipient, subject, template, context):
    """Render an HTML email and send it via the configured backend."""

    try:
        # Render the HTML email from the template and context.
        html = render_to_string(template, context)

        # Remove HTML tags to generate a plain text version.
        text = strip_tags(html)

        # Send the email using Django's configured email backend.
        send_mail(
            subject, text, settings.DEFAULT_FROM_EMAIL,
            [recipient], html_message=html, fail_silently=True,
        )

    # Ignore email-related errors so they do not interrupt application flow.
    except Exception:
        pass


# Notify the customer and staff when an order is placed.
def notify_order_placed(order):
    """Notify the customer and staff that an order was placed."""

    # Send customer notifications only if the order has an associated user.
    if order.user:
        # Create a database notification for the customer.
        _notify(
            order.user, NOTIFICATION_ORDER, 'Order placed',
            f'Your order {order.order_number} has been placed.',
            link=f'/orders/{order.id}/',
        )

        # Send an order confirmation email to the customer.
        _email(
            order.user.email, 'Order confirmation',
            'notifications/emails/order_placed.html', {'order': order},
        )

    # Staff broadcast.
    # Create a broadcast notification for staff.
    _notify(
        None, NOTIFICATION_ORDER, 'New order',
        f'New order {order.order_number} for {order.total}.',
    )


# Notify the customer when the order status changes.
def notify_order_status(order):
    """Notify the customer of an order status change."""

    # Exit if the order has no associated user.
    if not order.user:
        return

    # Create a notification with the updated order status.
    _notify(
        order.user, NOTIFICATION_ORDER, f'Order {order.get_status_display()}',
        f'Your order {order.order_number} is now {order.get_status_display()}.',
        link=f'/orders/{order.id}/',
    )


# Notify the customer about a payment event.
def notify_payment(payment):
    """Notify the customer of a payment event."""

    # Exit if the payment has no associated user.
    if not payment.user:
        return

    # Create a payment notification for the customer.
    _notify(
        payment.user, NOTIFICATION_PAYMENT, 'Payment update',
        f'Payment of {payment.amount} is {payment.get_status_display()}.',
        link=f'/orders/{payment.order_id}/' if payment.order_id else '',
    )


# Record a low stock alert and notify staff.
def notify_low_stock(product, variant, current_stock):
    """Persist a low-stock alert and notify staff."""

    # Determine the SKU from the variant if available, otherwise use the product SKU.
    sku = variant.sku if variant else product.sku

    # Build the display name including the variant when present.
    name = f'{product.name} ({variant.name})' if variant else product.name

    # Create and save a low stock alert record.
    LowStockAlert.objects.create(
        product_name=name, sku=sku, current_stock=current_stock,
    )

    # Create a broadcast notification for staff.
    _notify(
        None, NOTIFICATION_LOW_STOCK, 'Low stock alert',
        f'{name} is low on stock ({current_stock} left).',
    )


# Notify staff when a refund request is submitted.
def notify_refund_requested(refund):
    """Notify staff of a new refund request."""

    # Create a broadcast notification for the refund request.
    _notify(
        None, NOTIFICATION_ORDER, 'Refund requested',
        f'Refund requested for {refund.order.order_number}.',
    )


# Notify the customer when a refund has been processed.
def notify_refund_processed(refund):
    """Notify the customer that a refund was processed."""

    # Exit if the refund has no associated user.
    if not refund.user:
        return

    # Create a refund processed notification for the customer.
    _notify(
        refund.user, NOTIFICATION_PAYMENT, 'Refund processed',
        f'Your refund for {refund.order.order_number} was processed.',
        link=f'/orders/{refund.order_id}/',
