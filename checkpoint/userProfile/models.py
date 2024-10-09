from django.db import models

from login.models import CheckpointUser

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(CheckpointUser, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=100)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    bio = models.TextField(blank=True)

    def str(self):
        return self.display_name