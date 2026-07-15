# App configuration for the accounts app.

from django.apps import AppConfig


# Configure the accounts application.
class AccountsConfig(AppConfig):
    # Set up application settings.

    # Use BigAutoField as the default primary key type.
    default_auto_field = 'django.db.models.BigAutoField'

    # Application name.
    name = 'accounts'

    # Display name shown in the Django admin.
    verbose_name = 'Accounts'

    # Run application startup tasks.
    def ready(self):
        # Import signal handlers so they are registered.
        from . import signals  # noqa: F401
