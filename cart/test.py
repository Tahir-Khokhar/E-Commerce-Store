# Tests for the cart app.

from django.test import TestCase  # Django's built-in test class.
from django.urls import reverse  # Generates URLs from route names.

from rest_framework.test import APIClient  # Client for testing REST API endpoints.

# Import required models.
from accounts.models import User
from categories.models import Category
from products.models import Product, ProductVariant
from cart.models import Cart, CartItem


# Test cart functionality.
class CartFlowTest(TestCase):

    # Runs before every test.
    def setUp(self):

        # Create an API test client.
        self.client = APIClient()

        # Create a test user.
        self.user = User.objects.create_user(
            username='dave',
            email='dave@example.com',
            password='supersecret1'
        )

        # Create a test category.
        self.category = Category.objects.create(name='Toys')

        # Create a test product.
        self.product = Product.objects.create(
            name='Toy Car',
            sku='TY001',
            category=self.category,
            price=10.00,
            stock=5,
        )

        # Create a product variant.
        self.variant = ProductVariant.objects.create(
            product=self.product,
            sku='TY001-R',
            price=12.00,
            stock=3,
            name='Red'
        )

    # Test adding a product to the cart.
    def test_add_to_cart(self):

        # Get or create the user's cart.
        cart = Cart.get_or_create_cart(user=self.user)

        # Add two products.
        cart.add_item(self.product, 2)

        # Verify the total quantity.
        self.assertEqual(cart.item_count, 2)

        # Verify the subtotal.
        self.assertEqual(cart.subtotal, 20.00)

    # Test adding a product variant.
    def test_add_variant(self):

        # Get or create the user's cart.
        cart = Cart.get_or_create_cart(user=self.user)

        # Add one product variant.
        cart.add_item(self.product, 1, self.variant)

        # Verify the subtotal uses the variant price.
        self.assertEqual(cart.subtotal, 12.00)

        # first() returns the first cart item.
        self.assertEqual(cart.items.first().unit_price, 12.00)

    # Test merging a guest cart into a user's cart.
    def test_merge_guest_cart(self):

        # Import the merge helper.
        from cart.utils import merge_guest_cart

        # Create a guest cart.
        guest_cart = Cart.get_or_create_cart(session_key='sess123')

        # Add items to the guest cart.
        guest_cart.add_item(self.product, 3)

        # Merge the guest cart into the user's cart.
        merge_guest_cart(self.user, 'sess123')

        # Get the user's cart.
        user_cart = Cart.get_or_create_cart(user=self.user)

        # Verify the merged quantity.
        self.assertEqual(user_cart.item_count, 3)

        # exists() returns True if any matching record exists.
        # Verify the guest cart was deleted.
        self.assertFalse(
            Cart.objects.filter(session_key='sess123').exists()
        )

    # Test the cart API endpoint.
    def test_cart_api(self):

        # Log in the test user.
        self.client.force_authenticate(self.user)

        # Get the API URL.
        url = reverse('api-cart-add')

        # Send a POST request with JSON data.
        response = self.client.post(
            url,
            {
                'product_id': str(self.product.id),  # Convert UUID to string.
                'quantity': 2,
            },
            format='json'
        )

        # Verify the request succeeded.
        self.assertEqual(response.status_code, 200)

        # Verify two items were added.
        self.assertEqual(response.data['item_count'], 2)
