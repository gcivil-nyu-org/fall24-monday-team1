from django.db import models
from django.contrib.auth.models import User, AbstractUser

class CheckpointUser(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'username'  # Use email as the username
    REQUIRED_FIELDS = []  # Require username in addition to email