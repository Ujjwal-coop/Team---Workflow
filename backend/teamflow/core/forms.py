from django import forms
from django.contrib.auth.models import User
from .models import Task, EmployeeProfile


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(
        choices=[
            ("admin", "Admin / Manager"),
            ("employee", "Employee"),
        ]
    )


class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class TaskCreateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "employee", "deadline"]
