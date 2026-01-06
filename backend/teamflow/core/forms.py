from django import forms
from django.contrib.auth.models import User
from .models import Task, EmployeeProfile, ManagerProfile


# =========================
# LOGIN FORM
# =========================
class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
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
        widget=forms.PasswordInput(attrs={"class": "form-control"})
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

    class Meta:
        model = User
        fields = ["username", "password"]

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        manager = cleaned_data.get("manager")

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
# TASK CREATE FORM
# =========================
class TaskCreateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "employee", "deadline"]

    def __init__(self, *args, **kwargs):
        manager = kwargs.pop("manager", None)
        super().__init__(*args, **kwargs)

        # Restrict employees to the manager's own employees
        if manager:
            self.fields["employee"].queryset = EmployeeProfile.objects.filter(
                manager=manager
            )
