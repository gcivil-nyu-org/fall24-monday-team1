from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from ..models import UserProfile

@login_required
def user_profile_list(request):
    # Get query parameters
    query = request.GET.get('q', '')
    privacy = request.GET.get('privacy', '')
    role = request.GET.get('role', '')

    # Build the queryset
    queryset = UserProfile.objects.exclude(user=request.user)

    if query:
        queryset = queryset.filter(Q(display_name__icontains=query))

    if privacy:
        queryset = queryset.filter(privacy_setting=privacy)

    if role:
        queryset = queryset.filter(account_role=role)

    # Pagination
    paginator = Paginator(queryset, 6)  # Show 6 profiles per page
    page_number = request.GET.get('page')
    user_profiles = paginator.get_page(page_number)

    # Prepare context
    context = {
        'user_profiles': user_profiles,
        'query': query,
        'privacy': privacy,
        'role': role,
        'loginIn': True,
    }

    return render(request, 'userProfile/search_profile.html', context)