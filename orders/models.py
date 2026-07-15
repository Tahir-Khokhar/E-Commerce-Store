# Category models: hierarchical product categories.

from django.db import models  # Django model fields.
from django.utils.text import slugify  # Converts text into a URL-friendly slug.

# Import the shared active model.
from core.models import ActiveModel

# Import custom validator.
from core.validators import validate_non_negative


# Represents a product category.
class Category(ActiveModel):

    # Category name.
    name = models.CharField(max_length=100)

    # URL-friendly unique slug.
    # blank=True allows it to be generated automatically.
    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True
    )

    # Optional category description.
    description = models.TextField(blank=True)

    # Optional parent category for nested categories.
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,     # Delete child categories if the parent is deleted.
        null=True,
        blank=True,
        related_name='children'       # Access child categories using category.children.
    )

    # Optional category image.
    image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True
    )

    # Display order.
    order = models.PositiveIntegerField(default=0)

    # SEO title.
    meta_title = models.CharField(max_length=160, blank=True)

    # SEO description.
    meta_description = models.CharField(max_length=300, blank=True)

    # SEO keywords.
    meta_keywords = models.CharField(max_length=200, blank=True)

    class Meta:

        # Sort categories by order, then by name.
        ordering = ('order', 'name')

        # Singular model name.
        verbose_name = 'category'

        # Plural model name.
        verbose_name_plural = 'categories'

    # String representation of the category.
    def __str__(self):
        return self.name

    # Save the category.
    def save(self, *args, **kwargs):

        # Generate a slug if one doesn't already exist.
        if not self.slug:

            # slugify() converts text into a URL-friendly string.
            base = slugify(self.name) or 'category'

            # Start with the base slug.
            slug = base

            # Counter for duplicate slugs.
            n = 1

            # exists() returns True if a matching record exists.
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():

                # Add a number to make the slug unique.
                slug = f'{base}-{n}'

                n += 1

            # Save the unique slug.
            self.slug = slug

        # Call the parent save() method.
        super().save(*args, **kwargs)

    # Check whether this category has no parent.
    @property
    def is_parent(self):

        return self.parent is None

    # Return all parent categories.
    def get_ancestors(self):

        # Store parent categories.
        ancestors = []

        # Start with the direct parent.
        node = self.parent

        # Move up the category tree.
        while node:

            ancestors.append(node)

            node = node.parent

        # reversed() reverses the list order.
        # list() converts the reversed object into a list.
        return list(reversed(ancestors))
