from django import template
from django.shortcuts import get_object_or_404

from userProfile.models import UserProfile

register = template.Library()

@register.inclusion_tag('userProfile/navbar.html')
def render_navbar(user):
    if (user.is_authenticated):
        user.profile = get_object_or_404(UserProfile, user_id=user.pk)
    return {
        'user': user,
    }