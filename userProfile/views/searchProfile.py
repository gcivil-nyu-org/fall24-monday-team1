from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models import UserProfile
from django.db.models import Q

class UserProfileListView(LoginRequiredMixin, ListView):
    model = UserProfile
    template_name = 'userProfile/search_profile.html'
    context_object_name = 'user_profiles'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().exclude(user=self.request.user)
        query = self.request.GET.get('q')
        privacy = self.request.GET.get('privacy')
        role = self.request.GET.get('role')

        if query:
            queryset = queryset.filter(Q(display_name__icontains=query))

        if privacy:
            queryset = queryset.filter(privacy_setting=privacy)

        if role:
            queryset = queryset.filter(account_role=role)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['loginIn'] = True
        return context