from django import forms
from .models import DailyAssessment


class DailyAssessmentForm(forms.ModelForm):
    class Meta:
        model = DailyAssessment
        fields = ["beneficiary", "date", "notes"]
        widgets = {
            "beneficiary": forms.Select(attrs={"class": "form-select searchable", "data-placeholder": "ابحث باسم المستفيد أو رقمه..."}),
            "date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "notes": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
        }
