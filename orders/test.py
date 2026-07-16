"""Tests for the orders app checkout flow."""

# Import Django's base test case class for database-backed unit tests.
from django.test import TestCase

# Import reverse to generate URLs from named URL patterns.
from django.urls import reverse

# Import APIClient to simulate REST API requests in tests.
from rest_framework.test import APIClient

# Import the custom User model used for authentication.
from accounts.models import User
# Import the Category model used to organize products.
from categories.models import Category
# Import the Product model used for checkout testing.
from products.models import Product
# Import the Cart model used to manage shopping carts.
from cart.models import Cart
# Import Order and OrderItem models used in checkout tests.
from orders.models import Order, OrderItem


class CheckoutTest(TestCase):
    # Set up test data that is shared across all test methods.
    def setUp(self):
        # Create an API client for making test requests.
        self.client = APIClient()

        # Create a test user for authentication.
        self.user = User.objects.create_user(
            username='erin', email='erin@example.com', password='supersecret1'
        )

        # Create a product category for the test product.
        self.category = Category.objects.create(name='Books')

        # Create a test product with stock available.
        self.product = Product.objects.create(
            name='Novel', sku='NV001', category=self.category,
            price=20.00, stock=10,
        )

        # Get an existing cart or create a new one for the test user.
        self.cart = Cart.get_or_create_cart(user=self.user)

        # Add two units of the product to the cart.
        self.cart.add_item(self.product, 2)

    # Verify that checkout successfully creates an order.
    def test_checkout_creates_order(self):
        # Generate the checkout endpoint URL from its named route.
        url = reverse('api-checkout')

        # Authenticate the API client as the test user.
        self.client.force_authenticate(self.user)

        # Prepare valid checkout request data.
        data = {
            'shipping_full_name': 'Erin Doe',
            'shipping_line1': '123 Main St',
            'shipping_city': 'New York',
            'shipping_postal_code': '10001',
            'shipping_country': 'USA',
            'billing_same_as_shipping': True,
        }

        # Send a POST request to the checkout endpoint with JSON data.
        response = self.client.post(url, data, format='json')

        # Verify the checkout request completed successfully.
        self.assertEqual(response.status_code, 201)

        # Retrieve the order created for the test user.
        order = Order.objects.get(user=self.user)

        # Verify the order contains one item.
        self.assertEqual(order.items.count(), 1)

        # Verify the order subtotal is calculated correctly.
        self.assertEqual(order.subtotal, 40.00)

        # Verify the order total is calculated correctly.
        self.assertEqual(order.total, 40.00)

        # Stock decremented.

        # Reload the product from the database to get updated values.
        self.product.refresh_from_db()

        # Verify the product stock was reduced by the purchased quantity.
        self.assertEqual(self.product.stock, 8)

        # Cart cleared.

        # Verify the cart is empty after a successful checkout.
        self.assertEqual(self.cart.cart_items.count(), 0)

    # Verify that checkout fails when the cart is empty.
    def test_empty_cart_rejected(self):
        # Remove all items from the cart.
        self.cart.clear()

        # Generate the checkout endpoint URL from its named route.
        url = reverse('api-checkout')

        # Authenticate the API client as the test user.
        self.client.force_authenticate(self.user)

        # Prepare checkout data for an empty cart.
        data = {
            'shipping_full_name': 'Erin Doe',
            'shipping_line1': '123 Main St',
            'shipping_city': 'New York',
            'shipping_postal_code': '10001',
            'shipping_country': 'USA',
        }

        # Send a POST request to attempt checkout.
        response = self.client.post(url, data, format='json')

        # Verify the request is rejected with a bad request response.
        self.assertEqual(response.status_code, 400)

    # Verify that order status changes are recorded correctly.
    def test_order_status_history(self):
        # Create a new order with an initial pending status.
        order = Order.objects.create(user=self.user, status='pending')

        # Update the order status and record a status log entry.
        order.set_status('paid', note='paid')

        # Verify the order status was updated.
        self.assertEqual(order.status, 'paid')

        # Verify exactly one status history entry was created.
        self.assertEqual(order.status_logs.count(), 1)
