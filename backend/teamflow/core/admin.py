from django.contrib import admin
from .models import Task, ManagerProfile, EmployeeProfile


@admin.register(ManagerProfile)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name')


@admin.register(EmployeeProfile)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'manager')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'manager', 'employee', 'status', 'deadline')
    list_filter = ('status', 'manager')
    search_fields = ('title', 'employee__user__username')
