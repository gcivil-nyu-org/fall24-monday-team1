from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.RadioSelect(choices=[(i, f"{i} stars") for i in range(1, 6)]),
            "comment": forms.Textarea(attrs={"rows": 3}),
        }
