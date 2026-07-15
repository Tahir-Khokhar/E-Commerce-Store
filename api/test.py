# Tests for the API schema and endpoints.

from django.test import TestCase  # Django's built-in test class.
from django.urls import reverse  # Generates URLs using route names.

from rest_framework.test import APIClient  # Client used to test REST API endpoints.

# Import models used in the tests.
from categories.models import Category
from products.models import Product


# Test class for API endpoints.
class APITest(TestCase):

    # Runs before every test method.
    def setUp(self):

        # Create an API test client.
        self.client = APIClient()

        # Create a sample category.
        self.category = Category.objects.create(name='Tools')

        # Create a sample product.
        self.product = Product.objects.create(
            name='Hammer',
            sku='HM001',
            category=self.category,
            price=9.99
        )

    # Test whether the OpenAPI schema is available.
    def test_openapi_schema(self):

        # reverse() generates the URL from its route name.
        url = reverse('schema')

        # Send a GET request.
        response = self.client.get(url)

        # Check that the request was successful.
        self.assertEqual(response.status_code, 200)

        # Check that the response contains the OpenAPI schema.
        self.assertIn('openapi', response.data)

    # Test the category list endpoint.
    def test_category_list(self):

        # Get the category list URL.
        url = reverse('category-list')

        # Send a GET request.
        response = self.client.get(url)

        # Verify the request succeeded.
        self.assertEqual(response.status_code, 200)

        # Check that exactly one category exists.
        self.assertEqual(response.data['count'], 1)

    # Test filtering products by category.
    def test_product_filter_by_category(self):

        # Get the product list URL.
        url = reverse('product-list')

        # Send the category as a query parameter.
        self.client.get(url, {'category': 'tools'})

        # Store the response.
        response = self.client.get(url, {'category': 'tools'})

        # Verify the request succeeded.
        self.assertEqual(response.status_code, 200)

        # Check that one product matches the filter.
        self.assertEqual(response.data['count'], 1)

    # Test whether the Swagger documentation page loads.
    def test_swagger_ui(self):

        # Get the Swagger UI URL.
        url = reverse('swagger-ui')

        # Send a GET request.
        response = self.client.get(url)

        # Verify the page loads successfully.
        self.assertEqual(response.status_code, 200)
