from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User, Role, Permission


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="اسم المستخدم",
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "أدخل اسم المستخدم", "autofocus": True})
    )
    password = forms.CharField(
        label="كلمة المرور",
        widget=forms.PasswordInput(attrs={"class": "form-input", "placeholder": "أدخل كلمة المرور"})
    )


class UserForm(forms.ModelForm):
    password = forms.CharField(
        label="كلمة المرور", required=False,
        widget=forms.PasswordInput(attrs={"class": "form-input", "placeholder": "اتركها فارغة لعدم التغيير"})
    )

    class Meta:
        model = User
        fields = ["username", "full_name", "phone", "email", "role", "assigned_centers", "assigned_activities", "is_active"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-input"}),
            "full_name": forms.TextInput(attrs={"class": "form-input"}),
            "phone": forms.TextInput(attrs={"class": "form-input"}),
            "email": forms.EmailInput(attrs={"class": "form-input"}),
            "role": forms.Select(attrs={"class": "form-select"}),
            "assigned_centers": forms.CheckboxSelectMultiple(),
            "assigned_activities": forms.CheckboxSelectMultiple(),
            "is_active": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from centers.models import Activity
        self.fields["assigned_activities"].queryset = (
            Activity.objects.filter(is_active=True).select_related("center")
            .order_by("center__order", "center__name", "order", "name")
        )
        self.fields["assigned_activities"].label_from_instance = lambda a: f"{a.center.name} — {a.name}"

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
            self.save_m2m()
        return user


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ["name", "description", "permissions", "centers"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input"}),
            "description": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "permissions": forms.CheckboxSelectMultiple(),
            "centers": forms.CheckboxSelectMultiple(),
        }
