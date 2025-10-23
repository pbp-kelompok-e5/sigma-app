from django import forms
from .models import Review
from django.contrib.auth.models import User

class ReviewForm(forms.ModelForm):
    to_user = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label="Review For",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Review
        fields = ['to_user', 'rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }
