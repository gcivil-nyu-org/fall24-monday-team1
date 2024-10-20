from django.views.generic import ListView
from ..models import UserProfile
from django.db.models import Q

class UserProfileListView(ListView):
    model = UserProfile
    template_name = 'userprofile_list.html'
    context_object_name = 'user_profiles'
    paginate_by = 10  # Set pagination if needed

    def get_queryset(self):
        queryset = super().get_queryset()
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
        # Check if the user is logged in
        context['loginIn'] = self.request.user.is_authenticated  # Pass login status to template
        return context