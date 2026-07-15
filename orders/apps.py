# App configuration for the categories app.

from django.apps import AppConfig  # Base class for configuring a Django app.


# Configuration class for the categories app.
class CategoriesConfig(AppConfig):

    # Default type for automatically created primary keys.
    default_auto_field = 'django.db.models.BigAutoField'

    # Name of the Django app.
    name = 'categories'

    # Display name shown in the Django admin.
    verbose_name = 'Categories'
