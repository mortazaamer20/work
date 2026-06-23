from django import forms
from .models import DailyAssessment


class DailyAssessmentForm(forms.ModelForm):
    class Meta:
        model = DailyAssessment
        fields = ["beneficiary", "date", "attendance", "interaction_level", "mood", "appearance", "notes"]
        widgets = {
            "beneficiary": forms.Select(attrs={"class": "form-select"}),
            "date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "attendance": forms.Select(attrs={"class": "form-select"}),
            "interaction_level": forms.Select(attrs={"class": "form-select"}),
            "mood": forms.Select(attrs={"class": "form-select"}),
            "appearance": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
        }
