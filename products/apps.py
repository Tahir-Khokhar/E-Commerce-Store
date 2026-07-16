"""App configuration for the products app."""

# Import AppConfig to define application configuration.
from django.apps import AppConfig


# Application configuration for the products app.
class ProductsConfig(AppConfig):
    """Configuration for the products application."""

    # Specify the default type of auto-created primary key fields.
    default_auto_field = 'django.db.models.BigAutoField'

    # Define the Python path for this application.
    name = 'products'

    # Set the human-readable name displayed in the Django admin.
    verbose_name = 'Products'
