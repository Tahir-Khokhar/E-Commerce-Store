"""App configuration for the core app."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuration for the core application."""

    # Use BigAutoField as the default primary key and register the app.
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Core'
