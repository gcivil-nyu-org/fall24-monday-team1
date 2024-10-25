from django.db import models
from django.conf import settings

class Comment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    content = models.TextField(blank=True)  # Allow blank content for root comments
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)  # Keep this to track edits
    is_root = models.BooleanField(default=False)

    upvote = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='upvote_comments', blank=True)
    downvote = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='downvote_comments', blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.author} - {self.content[:20]}' if self.author else f'Anonymous - {self.content[:20]}'