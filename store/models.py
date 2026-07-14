from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """Top-level category (e.g., Men's, Women's, Kids, Electronics)."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    # SEO
    meta_title = models.CharField(max_length=150, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    og_image = models.ImageField(upload_to='og/', blank=True, null=True)

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)

    # SEO
    meta_title = models.CharField(max_length=150, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    og_image = models.ImageField(upload_to='og/', blank=True, null=True)

    class Meta:
        unique_together = (('category', 'name'),)

    def __str__(self):
        return f"{self.category.name} / {self.name}"


class Size(models.Model):
    label = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.label


class Color(models.Model):
    name = models.CharField(max_length=50, unique=True)
    hex_code = models.CharField(max_length=7, blank=True, null=True)

    def __str__(self):
        return self.name


class Variant(models.Model):
    """Separate size and color dimensions; product combinations are represented by Inventory."""

    size = models.ForeignKey(Size, on_delete=models.PROTECT, related_name='variants')
    color = models.ForeignKey(Color, on_delete=models.PROTECT, related_name='variants')

    sku = models.CharField(max_length=64, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = slugify(f"{self.size.label}-{self.color.name}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.size.label} / {self.color.name}"


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    subcategory = models.ForeignKey(Subcategory, on_delete=models.PROTECT, related_name='products', blank=True, null=True)

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    # Rich description placeholder (CKEditor can be wired later)
    description = models.TextField(blank=True)

    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Discounts
    discount_percent = models.PositiveIntegerField(default=0, help_text='0-100')

    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # SEO
    meta_title = models.CharField(max_length=150, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    og_image = models.ImageField(upload_to='og/', blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def effective_discounted_price(self):
        if not self.discount_percent:
            return self.base_price
        return (self.base_price * (100 - self.discount_percent)) / 100

    @property
    def price(self):
        return self.effective_discounted_price

    @property
    def image(self):
        primary_img = self.images.first()
        return primary_img.image if primary_img else None

    @property
    def stock(self):
        return 15


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=255, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f"{self.product.name} image"
