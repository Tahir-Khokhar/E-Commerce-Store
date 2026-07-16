"""Tests for the products app models and API."""

# Import Django's base test case class for database-backed unit tests.
from django.test import TestCase

# Import reverse to generate URLs from named URL patterns.
from django.urls import reverse

# Import APIClient to simulate REST API requests in tests.
from rest_framework.test import APIClient

# Import the Category model used to organize products.
from categories.models import Category

# Import product-related models used in the tests.
from products.models import Brand, Product, ProductImage, ProductVariant

# Import the Review model used to test product ratings.
from reviews.models import Review


# Test cases for Product model functionality.
class ProductModelTest(TestCase):
    # Set up common test data before each test method.
    def setUp(self):
        # Create a product category.
        self.category = Category.objects.create(name='Electronics')

        # Create a product brand.
        self.brand = Brand.objects.create(name='Samsung')

        # Create a sample product.
        self.product = Product.objects.create(
            name='Smartphone', sku='SP001', category=self.category,
            brand=self.brand, price=699.99, compare_at_price=799.99,
        )

    # Verify that a slug is automatically generated.
    def test_slug_generation(self):
        # Verify the generated slug matches the product name.
        self.assertEqual(self.product.slug, 'smartphone')

    # Verify that sale-related properties work correctly.
    def test_on_sale(self):
        # Verify the product is identified as being on sale.
        self.assertTrue(self.product.on_sale)

        # Verify a positive discount percentage is calculated.
        self.assertGreater(self.product.discount_percent, 0)

    # Verify the stock status updates correctly.
    def test_in_stock(self):
        # Set the product stock to zero.
        self.product.stock = 0

        # Save the updated product.
        self.product.save()

        # Verify the product is no longer considered in stock.
        self.assertFalse(self.product.in_stock)


# Test cases for the Product API.
class ProductAPITest(TestCase):
    # Set up common test data before each test method.
    def setUp(self):
        # Create an API client.
        self.client = APIClient()

        # Create a product category.
        self.category = Category.objects.create(name='Books')

        # Create a sample product.
        self.product = Product.objects.create(
            name='Django for Beginners', sku='BK001',
            category=self.category, price=29.99,
        )

    # Verify that the product list API returns products successfully.
    def test_product_list_api(self):
        # Generate the URL for the product list endpoint.
        url = reverse('product-list')

        # Send a GET request to the endpoint.
        response = self.client.get(url)

        # Verify the request completed successfully.
        self.assertEqual(response.status_code, 200)

        # Verify exactly one product is returned.
        self.assertEqual(response.data['count'], 1)

    # Verify that the average product rating is calculated correctly.
    def test_average_rating(self):
        # Import the User model for creating a review author.
        from accounts.models import User

        # Create a test user.
        user = User.objects.create_user(
            username='r',
            email='r@e.com',
            password='x',
        )

        # Create an approved review for the product.
        Review.objects.create(
            product=self.product,
            user=user,
            rating=4,
            title='Good',
            comment='Ok',
            status='approved',
        )

        # Verify the calculated average rating is correct.
        self.assertAlmostEqual(self.product.average_rating, 4.0)
