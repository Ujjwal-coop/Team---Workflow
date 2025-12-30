from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('progress', 'In Progress'),
        ('review', 'Review'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=200)
    deadline = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
