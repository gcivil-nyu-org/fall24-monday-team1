from django import template
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect

from userProfile.models import UserProfile

register = template.Library()

@register.inclusion_tag('userProfile/navbar.html')
def render_navbar(user):
    if (user.is_authenticated):
        try:
            user.profile = get_object_or_404(UserProfile, user_id=user.pk)
        except Http404:
            return redirect('createUserProfile:createProfile')
        
    return {
        'user': user,
    }