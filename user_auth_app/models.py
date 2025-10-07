from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """
    Extends the default Django User model with additional profile information.

    Fields:
    - user: One-to-one relationship with the Django User model.
    - bio: Optional text field for user biography.
    - location: Optional short text field for user's location.

    String representation returns the associated user's username.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.username