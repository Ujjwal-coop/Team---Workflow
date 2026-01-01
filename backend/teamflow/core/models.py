from django.db import models
from django.contrib.auth.models import User


class ManagerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)

    def __str__(self):
        return self.company_name


class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    manager = models.ForeignKey(
        ManagerProfile,
        on_delete=models.CASCADE,
        related_name='employees'
    )

    def __str__(self):
        return self.user.username


class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'Review'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    manager = models.ForeignKey(
        ManagerProfile,
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True,        # ✅ TEMPORARY FIX
        blank=True        # ✅ TEMPORARY FIX
    )

    employee = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True,        # ✅ already correct
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='todo'
    )

    deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
