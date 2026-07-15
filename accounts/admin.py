# Admin registrations for the accounts app.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Import all account-related models.
from accounts.models import User, Profile, Address, EmailVerification, PasswordResetToken


# Register the custom User model in the admin panel.
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Customize how the User model appears in the admin.

    # Columns displayed in the user list.
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_verified', 'is_staff', 'is_active')

    # Filters available in the admin sidebar.
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_verified')

    # Fields used for searching users.
    search_fields = ('email', 'username', 'first_name', 'last_name')

    # Sort users by newest first.
    ordering = ('-date_joined',)

    # Make these fields read-only.
    readonly_fields = ('created_at', 'updated_at', 'last_login')

    # Organize fields into sections.
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone', 'date_of_birth')}),
        ('Permissions', {'fields': ('is_active', 'is_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    # Fields shown when adding a new user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )


# Display addresses as inline records.
class AddressInline(admin.TabularInline):
    # Configure inline editing for addresses.

    # Address model used in the inline.
    model = Address

    # Do not show extra empty forms.
    extra = 0

    # Fields displayed in the inline form.
    fields = ('address_type', 'full_name', 'line1', 'city', 'country', 'is_default')


# Register the Profile model in the admin panel.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # Customize how profiles appear in the admin.

    # Columns displayed in the profile list.
    list_display = ('user', 'newsletter', 'created_at')

    # Fields used for searching profiles.
    search_fields = ('user__email', 'user__username')

    # No inline models included.
    inlines = []


# Register the Address model in the admin panel.
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    # Customize how addresses appear in the admin.

    # Columns displayed in the address list.
    list_display = ('user', 'address_type', 'full_name', 'city', 'country', 'is_default')

    # Filters available for addresses.
    list_filter = ('address_type', 'country', 'is_default')

    # Fields used for searching addresses.
    search_fields = ('full_name', 'city', 'user__email')

    # Make timestamps read-only.
    readonly_fields = ('created_at', 'updated_at')


# Register the EmailVerification model in the admin panel.
@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    # Customize email verification records.

    # Columns displayed in the verification list.
    list_display = ('user', 'verified', 'expires_at')

    # Filter records by verification status.
    list_filter = ('verified',)

    # Search by user email.
    search_fields = ('user__email',)

    # Prevent editing of token and expiry.
    readonly_fields = ('token', 'expires_at')


# Register the PasswordResetToken model in the admin panel.
@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    # Customize password reset token records.

    # Columns displayed in the token list.
    list_display = ('user', 'used', 'expires_at')

    # Filter records by usage status.
    list_filter = ('used',)

    # Search by user email.
    search_fields = ('user__email',)

    # Prevent editing of token and expiry.
    readonly_fields = ('token', 'expires_at')
