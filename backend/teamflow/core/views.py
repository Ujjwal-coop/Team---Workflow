from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

from .models import Task
from .forms import TaskCreateForm, TaskUpdateForm


# =========================
# LOGIN
# =========================
def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )

        if user:
            login(request, user)
            return redirect('manager_dashboard' if user.is_staff else 'dashboard')

        messages.error(request, "Invalid username or password")

    return render(request, 'login.html')


# =========================
# USER DASHBOARD
# =========================
@login_required
def dashboard(request):
    tasks = Task.objects.filter(assigned_to=request.user)

    return render(request, 'dashboard.html', {
        'tasks': tasks[:5],  # recent tasks
        'total': tasks.count(),
        'pending': tasks.exclude(status='completed').count(),
        'completed': tasks.filter(status='completed').count(),
    })


# =========================
# USER TASK LIST
# =========================
@login_required
def task_list(request):
    tasks = Task.objects.filter(assigned_to=request.user)
    return render(request, 'task_list.html', {'tasks': tasks})


# =========================
# UPDATE TASK STATUS (USER)
# =========================
@login_required
def task_update(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)

    if request.method == 'POST':
        form = TaskUpdateForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task status updated successfully")
            return redirect('task_list')
    else:
        form = TaskUpdateForm(instance=task)

    return render(request, 'task_update.html', {
        'task': task,
        'form': form
    })


# =========================
# MANAGER DASHBOARD
# =========================
@staff_member_required
def manager_dashboard(request):
    tasks = Task.objects.all()

    return render(request, 'manager_dashboard.html', {
        'tasks': tasks,
        'total': tasks.count(),
        'pending': tasks.exclude(status='completed').count(),
        'completed': tasks.filter(status='completed').count(),
    })


# =========================
# CREATE TASK (MANAGER)
# =========================
@staff_member_required
def create_task(request):
    if request.method == 'POST':
        form = TaskCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Task created successfully")
            return redirect('manager_dashboard')
    else:
        form = TaskCreateForm()

    return render(request, 'create_task.html', {'form': form})


# =========================
# LOGOUT
# =========================
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
