from django import template
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse

from userProfile.models import UserProfile

register = template.Library()

@register.simple_tag
def render_user_info(user_id):
    user_profile = get_object_or_404(UserProfile, user_id=user_id)
    if not user_profile:
        return ""

    # Render the user info HTML using the template
    return render_to_string('userProfile/user_info.html', 
                            {'user_profile': user_profile,
                             "profile_link": reverse('userProfile:viewProfile', 
                                                    args=[user_id])})