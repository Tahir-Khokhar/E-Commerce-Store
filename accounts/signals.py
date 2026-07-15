# Accounts signals: automatically create a profile after a user is created.

from django.db.models.signals import post_save  # Signal sent after a model is saved.
from django.dispatch import receiver  # Decorator used to register signal functions.

# Import the models used by the signal.
from accounts.models import User, Profile


# Register this function to run after a User object is saved.
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):

    # Check whether this is a newly created user.
    if created:

        # get_or_create() returns an existing profile or creates a new one.
        Profile.objects.get_or_create(user=instance)
