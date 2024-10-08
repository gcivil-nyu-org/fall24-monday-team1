from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', default='default.jpg')
    gaming_platform = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'