from django import forms
from .models import Feedback


class FeedbackForm(forms.ModelForm):
    RATING_CHOICES = (
        (5, '★★★★★ (5/5) - Excellent & Fast Resolution'),
        (4, '★★★★☆ (4/5) - Very Good Resolution'),
        (3, '★★★☆☆ (3/5) - Satisfactory / Acceptable'),
        (2, '★★☆☆☆ (2/5) - Needs Improvement'),
        (1, '★☆☆☆☆ (1/5) - Poor Resolution / Unsatisfactory'),
    )

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select form-select-lg', 'required': 'required'})
    )
    comments = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Share your feedback on the resolution quality, response speed, and officer conduct...',
            'required': 'required'
        })
    )

    class Meta:
        model = Feedback
        fields = ('rating', 'comments')
