"""Reusable mixins for views and serializers."""

from django.utils.text import slugify


class SlugMixin:
    """Generate a slug from a source field before saving."""

    slug_source_field = 'name'
    slug_field = 'slug'

    def save(self, *args, **kwargs):
        # Get the source field value safely.
        source = getattr(self, self.slug_source_field, '')

        # Create a slug if it does not already exist.
        if source and not getattr(self, self.slug_field, None):

            # Set the generated slug value.
            setattr(self, self.slug_field, slugify(source))

        # Save the model instance.
        super().save(*args, **kwargs)
