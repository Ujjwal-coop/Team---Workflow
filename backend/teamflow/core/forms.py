from django import forms
from .models import Task, EmployeeProfile


# =========================
# MANAGER: CREATE TASK
# =========================
class TaskCreateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'employee', 'deadline']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        manager = kwargs.pop('manager')
        super().__init__(*args, **kwargs)

        # Only employees under this manager
        self.fields['employee'].queryset = EmployeeProfile.objects.filter(
            manager=manager
        )


# =========================
# EMPLOYEE: UPDATE TASK
# =========================
class TaskUpdateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'})
        }