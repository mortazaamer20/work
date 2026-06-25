from django import forms
from .models import Center, Activity, ActivityField, Clinic, ClinicField, GeneralField


class GeneralFieldForm(forms.ModelForm):
    class Meta:
        model = GeneralField
        fields = ["name", "field_key", "field_type", "choices_text", "is_required",
                  "max_score", "counts_in_score", "is_active", "order"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input"}),
            "field_key": forms.TextInput(attrs={"class": "form-input", "dir": "ltr"}),
            "field_type": forms.Select(attrs={"class": "form-select"}),
            "choices_text": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "max_score": forms.NumberInput(attrs={"class": "form-input"}),
            "order": forms.NumberInput(attrs={"class": "form-input"}),
        }


class CenterForm(forms.ModelForm):
    class Meta:
        model = Center
        fields = ["name", "slug", "description", "icon", "color", "weight", "axis", "is_active", "order"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input"}),
            "slug": forms.TextInput(attrs={"class": "form-input", "dir": "ltr"}),
            "description": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "icon": forms.TextInput(attrs={"class": "form-input", "dir": "ltr"}),
            "color": forms.TextInput(attrs={"class": "form-input", "type": "color"}),
            "weight": forms.NumberInput(attrs={"class": "form-input"}),
            "axis": forms.Select(attrs={"class": "form-select"}),
            "order": forms.NumberInput(attrs={"class": "form-input"}),
        }


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ["center", "name", "slug", "description", "is_active", "order"]
        widgets = {
            "center": forms.Select(attrs={"class": "form-select"}),
            "name": forms.TextInput(attrs={"class": "form-input"}),
            "slug": forms.TextInput(attrs={"class": "form-input", "dir": "ltr"}),
            "description": forms.Textarea(attrs={"class": "form-input", "rows": 2}),
            "order": forms.NumberInput(attrs={"class": "form-input"}),
        }


class ActivityFieldForm(forms.ModelForm):
    class Meta:
        model = ActivityField
        fields = ["name", "field_key", "field_type", "choices_text", "is_required", "max_score", "order"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input"}),
            "field_key": forms.TextInput(attrs={"class": "form-input", "dir": "ltr"}),
            "field_type": forms.Select(attrs={"class": "form-select"}),
            "choices_text": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "max_score": forms.NumberInput(attrs={"class": "form-input"}),
            "order": forms.NumberInput(attrs={"class": "form-input"}),
        }


class ClinicForm(forms.ModelForm):
    class Meta:
        model = Clinic
        fields = ["center", "name", "slug", "description", "is_active", "order"]
        widgets = {
            "center": forms.Select(attrs={"class": "form-select"}),
            "name": forms.TextInput(attrs={"class": "form-input"}),
            "slug": forms.TextInput(attrs={"class": "form-input", "dir": "ltr"}),
            "description": forms.Textarea(attrs={"class": "form-input", "rows": 2}),
            "order": forms.NumberInput(attrs={"class": "form-input"}),
        }


class ClinicFieldForm(forms.ModelForm):
    class Meta:
        model = ClinicField
        fields = ["name", "field_key", "field_type", "choices_text", "is_required", "unit", "normal_min", "normal_max", "order"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input"}),
            "field_key": forms.TextInput(attrs={"class": "form-input", "dir": "ltr"}),
            "field_type": forms.Select(attrs={"class": "form-select"}),
            "choices_text": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "unit": forms.TextInput(attrs={"class": "form-input"}),
            "normal_min": forms.NumberInput(attrs={"class": "form-input"}),
            "normal_max": forms.NumberInput(attrs={"class": "form-input"}),
            "order": forms.NumberInput(attrs={"class": "form-input"}),
        }
