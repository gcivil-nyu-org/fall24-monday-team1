from django import forms
from userProfile.models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['display_name', 'profile_photo', 'bio', 'gaming_usernames', 'privacy_setting', 'account_role']
