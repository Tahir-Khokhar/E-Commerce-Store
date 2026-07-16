"""Tests for the payments app."""

# Import Django's base test case class for database-backed unit tests.
from django.test import TestCase

# Import the custom User model for creating test users.
from accounts.models import User

# Import the Category model for creating product categories.
from categories.models import Category

# Import the Product model for creating test products.
from products.models import Product

# Import the Order model used in payment tests.
from orders.models import Order

# Import the Payment model used to create payment records.
from payments.models import Payment

# Import payment service functions under test.
from payments.services import create_payment, refund_payment


# Test cases for payment-related functionality.
class PaymentTest(TestCase):
    # Set up common test data before each test method.
    def setUp(self):
        # Create a test user.
        self.user = User.objects.create_user(
            username='frank', email='frank@example.com', password='supersecret1'
        )

        # Create a product category.
        self.category = Category.objects.create(name='Books')

        # Create a sample product.
        self.product = Product.objects.create(
            name='Book', sku='BK002', category=self.category, price=15.00
        )

        # Create a pending order for the test user.
        self.order = Order.objects.create(
            user=self.user, status='pending', subtotal=15.00, total=15.00
        )

    # Verify that a Cash on Delivery payment remains pending.
    def test_cod_payment_pending(self):
        # Create a COD payment.
        result = create_payment(self.order, 'cod')

        # Retrieve the created payment.
        payment = result['payment']

        # Verify the payment method is COD.
        self.assertEqual(payment.method, 'cod')

        # Verify the payment status is pending.
        self.assertEqual(payment.status, 'pending')

        # Verify the response identifies this as a COD payment.
        self.assertTrue(result['cod'])

    # Verify that completing a payment advances the related order status.
    def test_mark_completed_advances_order(self):
        # Create a pending payment.
        payment = Payment.objects.create(
            order=self.order, user=self.user, method='cod',
            amount=15.00, status='pending',
        )

        # Mark the payment as completed.
        payment.mark_completed()

        # Reload the order from the database.
        self.order.refresh_from_db()

        # Verify the payment status was updated.
        self.assertEqual(payment.status, 'completed')

        # Verify the order status advanced to paid.
        self.assertEqual(self.order.status, 'paid')

    # Verify that refunding a payment updates the order and payment status.
    def test_refund_marks_order_refunded(self):
        # Create a completed payment.
        payment = Payment.objects.create(
            order=self.order, user=self.user, method='cod',
            amount=15.00, status='completed',
        )

        # Process a full refund.
        refund_payment(payment, 15.00)

        # Reload the order from the database.
        self.order.refresh_from_db()

        # Verify the order status is refunded.
        self.assertEqual(self.order.status, 'refunded')

        # Verify the payment status is refunded.
        self.assertEqual(payment.status, 'refunded')
