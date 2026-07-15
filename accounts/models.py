# Accounts models: custom user, profile, address book, and authentication tokens.

import uuid  # Used to generate unique UUID values.

from django.contrib.auth.models import AbstractUser  # Django's built-in user model.
from django.db import models  # Provides Django model fields.
from django.utils import timezone  # Used for timezone-aware date and time.
from django.utils.translation import gettext_lazy as _  # Marks text for translation.

# Import the shared base model.
from core.models import BaseModel

# Import custom phone number validator.
from core.validators import validate_phone


# Custom user model extending Django's AbstractUser.
class User(AbstractUser):
    # Store UUID instead of an auto-incrementing integer as the primary key.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # User email must be unique.
    email = models.EmailField(_('email address'), unique=True)

    # Optional phone number with custom validation.
    phone = models.CharField(max_length=20, blank=True, validators=[validate_phone])

    # Tracks whether the email has been verified.
    is_verified = models.BooleanField(default=False)

    # Stores the email verification token.
    email_verification_token = models.CharField(max_length=100, blank=True)

    # Optional date of birth.
    date_of_birth = models.DateField(null=True, blank=True)

    # Automatically set when the record is created.
    created_at = models.DateTimeField(auto_now_add=True)

    # Automatically updated whenever the record is saved.
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Show newest users first.
        ordering = ('-date_joined',)

        # Singular name used in the Django admin.
        verbose_name = _('user')

        # Plural name used in the Django admin.
        verbose_name_plural = _('users')

    # Returns a readable string when the object is printed.
    def __str__(self):
        return self.email or self.username

    # Create a full name property that can be accessed like an attribute.
    @property
    def full_name(self):
        # Remove extra spaces using strip() and return username if name is empty.
        return f'{self.first_name} {self.last_name}'.strip() or self.username


# Stores additional information for each user.
class Profile(BaseModel):

    # One profile belongs to one user.
    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,      # Delete profile if user is deleted.
        related_name='profile'         # Access profile using user.profile.
    )

    # Optional profile image.
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    # User biography.
    bio = models.TextField(max_length=500, blank=True)

    # Newsletter subscription status.
    newsletter = models.BooleanField(default=True)

    # Human-readable object representation.
    def __str__(self):
        return f'Profile of {self.user}'


# Stores shipping and billing addresses.
class Address(BaseModel):

    # Available address types.
    ADDRESS_TYPES = (
        ('shipping', _('Shipping')),
        ('billing', _('Billing')),
    )

    # One user can have many addresses.
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,       # Delete addresses if user is deleted.
        related_name='addresses'        # Access addresses using user.addresses.
    )

    # Shipping or billing address.
    address_type = models.CharField(
        max_length=10,
        choices=ADDRESS_TYPES,          # Creates a dropdown in forms/admin.
        default='shipping'
    )

    # Full name of the recipient.
    full_name = models.CharField(max_length=150)

    # Optional phone number.
    phone = models.CharField(max_length=20, blank=True, validators=[validate_phone])

    # First address line.
    line1 = models.CharField(max_length=255)

    # Optional second address line.
    line2 = models.CharField(max_length=255, blank=True)

    # City name.
    city = models.CharField(max_length=100)

    # Optional state or province.
    state = models.CharField(max_length=100, blank=True)

    # Postal or ZIP code.
    postal_code = models.CharField(max_length=20)

    # Country name.
    country = models.CharField(max_length=100)

    # Marks this address as the default one.
    is_default = models.BooleanField(default=False)

    class Meta:
        # Show default addresses first, then newest.
        ordering = ('-is_default', '-created_at')

    # Returns the address in a readable format.
    def __str__(self):
        return f'{self.full_name} - {self.city}'

    # Override Django's save() method.
    def save(self, *args, **kwargs):

        # Allow only one default address for each user and address type.
        if self.is_default:

            # Find other default addresses.
            Address.objects.filter(
                user=self.user,
                address_type=self.address_type,
                is_default=True
            ) \
            .exclude(pk=self.pk) \      # Skip the current object.
            .update(is_default=False)   # Make others non-default.

        # Call the original save() method.
        super().save(*args, **kwargs)


# Stores email verification tokens.
class EmailVerification(BaseModel):

    # One verification record belongs to one user.
    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='email_verification'
    )

    # Unique verification token.
    token = models.CharField(max_length=100, unique=True)

    # Expiry date and time.
    expires_at = models.DateTimeField()

    # Indicates whether the email has been verified.
    verified = models.BooleanField(default=False)

    # Check whether the token has expired.
    def is_expired(self):
        # timezone.now() returns the current timezone-aware datetime.
        return timezone.now() > self.expires_at

    # Human-readable object representation.
    def __str__(self):
        return f'Verification for {self.user}'


# Stores password reset tokens.
class PasswordResetToken(BaseModel):

    # One user can have multiple reset tokens.
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='reset_tokens'
    )

    # Unique password reset token.
    token = models.CharField(max_length=100, unique=True)

    # Expiry date and time.
    expires_at = models.DateTimeField()

    # Tracks whether the token has already been used.
    used = models.BooleanField(default=False)

    # Check whether the token has expired.
    def is_expired(self):
        return timezone.now() > self.expires_at

    # Human-readable object representation.
    def __str__(self):
        return f'Reset token for {self.user}'
