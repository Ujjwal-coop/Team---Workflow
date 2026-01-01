from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

from .models import Task, ManagerProfile, EmployeeProfile
from .forms import TaskCreateForm, TaskUpdateForm


# =========================
# LOGIN VIEW
# =========================
def login_view(request):
    managers = ManagerProfile.objects.all()

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        manager_id = request.POST.get("manager")

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid username or password")
            return render(request, 'login.html', {'managers': managers})

        login(request, user)

        # ADMIN
        if user.is_superuser:
            return redirect('/admin/')

        # MANAGER
        if hasattr(user, 'managerprofile'):
            return redirect('manager_dashboard')

        # EMPLOYEE
        if hasattr(user, 'employeeprofile'):
            if not manager_id:
                messages.error(request, "Please select your manager")
                logout(request)
                return render(request, 'login.html', {'managers': managers})

            if int(manager_id) != user.employeeprofile.manager.id:
                messages.error(request, "Incorrect manager selected")
                logout(request)
                return render(request, 'login.html', {'managers': managers})

            return redirect('dashboard')

        messages.error(request, "Unauthorized account")
        logout(request)

    return render(request, 'login.html', {'managers': managers})


# =========================
# LOGOUT
# =========================
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


# =========================
# EMPLOYEE DASHBOARD
# =========================
@login_required
def dashboard(request):
    employee = request.user.employeeprofile
    tasks = employee.tasks.all()

    return render(request, 'dashboard.html', {
        'tasks': tasks,
        'total': tasks.count(),
        'pending': tasks.exclude(status='completed').count(),
        'completed': tasks.filter(status='completed').count(),
    })


# =========================
# EMPLOYEE TASK LIST
# =========================
@login_required
def task_list(request):
    employee = request.user.employeeprofile
    tasks = employee.tasks.all()

    return render(request, 'task_list.html', {'tasks': tasks})


# =========================
# EMPLOYEE TASK UPDATE
# =========================
@login_required
def task_update(request, task_id):
    employee = request.user.employeeprofile
    task = get_object_or_404(Task, id=task_id, employee=employee)

    if request.method == "POST":
        form = TaskUpdateForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated successfully")
            return redirect('dashboard')
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
    manager = request.user.managerprofile
    tasks = manager.tasks.all()

    return render(request, 'manager_dashboard.html', {
        'tasks': tasks,
        'employees_count': manager.employees.count(),
        'total': tasks.count(),
        'pending': tasks.exclude(status='completed').count(),
        'completed': tasks.filter(status='completed').count(),
    })


# =========================
# MANAGER CREATE TASK
# =========================
@staff_member_required
def create_task(request):
    manager = request.user.managerprofile

    if request.method == "POST":
        form = TaskCreateForm(request.POST, manager=manager)
        if form.is_valid():
            task = form.save(commit=False)
            task.manager = manager
            task.save()
            messages.success(request, "Task created successfully")
            return redirect('manager_dashboard')
    else:
        form = TaskCreateForm(manager=manager)

    return render(request, 'create_task.html', {'form': form})