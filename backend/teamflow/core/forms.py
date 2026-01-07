# core/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import Task, EmployeeProfile, ManagerProfile


# =========================
# LOGIN FORM
# =========================
class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control",
            "placeholder": "Username"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control",
            "placeholder": "Password"})
    )
    role = forms.ChoiceField(
        choices=[
            ("admin", "Admin / Manager"),
            ("employee", "Employee"),
        ],
        widget=forms.HiddenInput()
    )
    manager = forms.ModelChoiceField(
        queryset=ManagerProfile.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )


# =========================
# SIGNUP FORM
# =========================
class SignUpForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control",
            "placeholder": "Password"})
    )

    role = forms.ChoiceField(
        choices=[
            ("manager", "Manager"),
            ("employee", "Employee"),
        ],
        widget=forms.HiddenInput()
    )

    manager = forms.ModelChoiceField(
        queryset=ManagerProfile.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )

      # NEW: Company name for manager signup
    company_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Company Name"
        })
    )

    class Meta:
        model = User
        fields = ["username", "password"]

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        manager = cleaned_data.get("manager")
        company_name = cleaned_data.get("company_name")

        if role == "manager" and not company_name:
            raise forms.ValidationError(
                "Company name is required for manager signup."
            )

        if role == "employee" and not manager:
            raise forms.ValidationError("Employee must select a manager.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


# =========================
# TASK CREATE FORM (FIXED)
# =========================
class TaskCreateForm(forms.ModelForm):

    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 4,
            "placeholder": "Write instructions or message for employee..."
        })
    )

    deadline = forms.DateField(
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "form-control"
        })
    )

    class Meta:
        model = Task
        fields = ["title", "description", "employee", "deadline"]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Task title"
            }),
            "employee": forms.Select(attrs={
                "class": "form-select"
            }),
        }

    def __init__(self, *args, **kwargs):
        manager = kwargs.pop("manager", None)
        super().__init__(*args, **kwargs)

        if manager:
            self.fields["employee"].queryset = EmployeeProfile.objects.filter(
                manager=manager
            )
