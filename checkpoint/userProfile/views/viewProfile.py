from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from ..models import UserProfile

def viewProfile(request, user_id):
    profile = get_object_or_404(UserProfile, user__id=user_id)
    return render(request, 'profileView.html', {'profile': profile})