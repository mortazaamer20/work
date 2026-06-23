from django import forms
from .models import Beneficiary


class BeneficiaryForm(forms.ModelForm):
    class Meta:
        model = Beneficiary
        fields = [
            "ref_number", "full_name", "gender", "date_of_birth",
            "national_id", "phone", "emergency_contact", "emergency_phone",
            "address", "admission_date", "expected_discharge_date", "status",
            "admission_reason", "notes", "photo",
        ]
        widgets = {
            "ref_number": forms.TextInput(attrs={"class": "form-input"}),
            "full_name": forms.TextInput(attrs={"class": "form-input"}),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "date_of_birth": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "national_id": forms.TextInput(attrs={"class": "form-input"}),
            "phone": forms.TextInput(attrs={"class": "form-input"}),
            "emergency_contact": forms.TextInput(attrs={"class": "form-input"}),
            "emergency_phone": forms.TextInput(attrs={"class": "form-input"}),
            "address": forms.Textarea(attrs={"class": "form-input", "rows": 2}),
            "admission_date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "expected_discharge_date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "admission_reason": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "notes": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
        }
