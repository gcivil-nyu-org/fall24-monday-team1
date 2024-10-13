from django.db import models

from login.models import CheckpointUser

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(CheckpointUser, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=100)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    bio = models.TextField(blank=True)
    gaming_usernames = models.JSONField(blank=True, null=True)  # Store usernames for different platforms
    privacy_setting = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('friends_only', 'Friends Only'),
            ('private', 'Private'),
        ],
        default='public'
    )
    account_role = models.CharField(
        max_length=20,
        choices=[
            ('gamer', 'Gamer'),
            ('creator', 'Creator'),
            ('event_organizer', 'Event Organizer')
        ],
        default='gamer'
    )

    def str(self):
        return self.display_name +" " + self.account_role