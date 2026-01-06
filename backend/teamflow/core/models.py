from django.db import models
from django.contrib.auth.models import User


class ManagerProfile(models.Model):
    """
    Manager profile linked one-to-one with Django User.
    Each manager can have multiple employees and tasks.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="manager_profile"
    )
    company_name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.company_name} ({self.user.username})"


class EmployeeProfile(models.Model):
    """
    Employee profile linked to a User and assigned to a Manager.
    Each employee belongs to exactly one manager.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="employee_profile"
    )
    manager = models.ForeignKey(
        ManagerProfile,
        on_delete=models.CASCADE,
        related_name="employees"
    )

    def __str__(self):
        return f"{self.user.username} → {self.manager.company_name}"


class Task(models.Model):
    """
    Task created by a Manager and assigned to an Employee.
    Admin has full access via superuser privileges.
    """

    STATUS_CHOICES = [
        ("todo", "To Do"),
        ("in_progress", "In Progress"),
        ("review", "Review"),
        ("completed", "Completed"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    manager = models.ForeignKey(
        ManagerProfile,
        on_delete=models.CASCADE,
        related_name="tasks"
    )

    employee = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name="tasks"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="todo"
    )

    deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.employee.user.username})"
