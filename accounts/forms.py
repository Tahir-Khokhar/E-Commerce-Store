# HTML forms for the accounts web interface.

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

# Import models used in the forms.
from accounts.models import Profile, Address

# Get the active User model.
User = get_user_model()


# Form for registering a new user.
class RegistrationForm(UserCreationForm):
    # Collect user registration details.

    # Required email field.
    email = forms.EmailField(required=True)

    # Optional phone number field.
    phone = forms.CharField(required=False, max_length=20)

    class Meta:
        # Use the custom User model.
        model = User

        # Fields included in the registration form.
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2')


# Form for user login.
class LoginForm(forms.Form):
    # Accept either username or email.
    username = forms.CharField(label='Username or email', max_length=150)

    # Password input field.
    password = forms.CharField(widget=forms.PasswordInput)


# Form for editing user profile information.
class ProfileForm(forms.ModelForm):
    # Additional user fields.

    # First name field.
    first_name = forms.CharField(required=False, max_length=150)

    # Last name field.
    last_name = forms.CharField(required=False, max_length=150)

    # Required email field.
    email = forms.EmailField(required=True)

    # User biography field.
    bio = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}))

    # Newsletter subscription option.
    newsletter = forms.BooleanField(required=False)

    # Profile picture upload.
    avatar = forms.ImageField(required=False)

    class Meta:
        # Use the Profile model.
        model = Profile

        # Editable profile fields.
        fields = ('avatar', 'bio', 'newsletter')

    # Initialize the form with user data.
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        # Pre-fill user information.
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email

    # Save profile and user information.
    def save(self, commit=True):
        # Save the profile without committing immediately.
        profile = super().save(commit=False)

        # Update user information.
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']

            # Save the user if requested.
            if commit:
                self.user.save()

        # Save the profile if requested.
        if commit:
            profile.save()

        # Return the saved profile.
        return profile


# Form for creating or editing an address.
class AddressForm(forms.ModelForm):
    # Address details form.

    class Meta:
        # Use the Address model.
        model = Address

        # Editable address fields.
        fields = (
            'address_type', 'full_name', 'phone', 'line1', 'line2',
            'city', 'state', 'postal_code', 'country', 'is_default',
        )


# Form for requesting a password reset.
class PasswordResetRequestForm(forms.Form):
    # Email address for password reset.
    email = forms.EmailField()


# Form for confirming a password reset.
class PasswordResetConfirmForm(forms.Form):
    # New password field.
    password1 = forms.CharField(widget=forms.PasswordInput)

    # Confirm new password field.
    password2 = forms.CharField(widget=forms.PasswordInput)

    # Check that both passwords match.
    def clean(self):
        cleaned = super().clean()

        # Raise an error if passwords are different.
        if cleaned.get('password1') != cleaned.get('password2'):
            raise forms.ValidationError('Passwords do not match.')

        # Return validated data.
        return cleaned
