# Authentication backend that accepts username or email.

from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

# Import the custom User model.
from accounts.models import User


# Allow users to log in using either username or email.
class EmailOrUsernameBackend(ModelBackend):
    # Custom authentication backend.

    # Authenticate a user with a username/email and password.
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Get the username from kwargs if not provided directly.
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)

        # Stop if username or password is missing.
        if username is None or password is None:
            return None

        try:
            # Find a user by username or email.
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )

        # Return None if no matching user exists.
        except User.DoesNotExist:
            # Hash the password to reduce timing attacks.
            User().set_password(password)
            return None

        # Return None if multiple matching users are found.
        except User.MultipleObjectsReturned:
            return None

        # Return the user if the password is correct and the account is active.
        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        # Authentication failed.
        return None


# Backward-compatible alias for the authentication backend.
class EmailBackend(EmailOrUsernameBackend):
    # Inherits all functionality from EmailOrUsernameBackend.
    pass
