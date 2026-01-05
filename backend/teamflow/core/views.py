from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Task, ManagerProfile, EmployeeProfile
from .forms import TaskCreateForm


# =========================
# LOGIN
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
            return render(request, "login.html", {"managers": managers})

        login(request, user)

        # ADMIN
        if user.is_superuser:
            return redirect("/admin/")

        # MANAGER
        if hasattr(user, "managerprofile"):
            return redirect("manager_dashboard")

        # EMPLOYEE
        if hasattr(user, "employeeprofile"):
            if not manager_id:
                messages.error(request, "Please select your manager")
                logout(request)
                return render(request, "login.html", {"managers": managers})

            if int(manager_id) != user.employeeprofile.manager.id:
                messages.error(request, "Incorrect manager selected")
                logout(request)
                return render(request, "login.html", {"managers": managers})

            return redirect("dashboard")

        messages.error(request, "Unauthorized account")
        logout(request)

    return render(request, "login.html", {"managers": managers})


# =========================
# LOGOUT
# =========================
@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


# =========================
# EMPLOYEE DASHBOARD
# =========================
@login_required
def dashboard(request):
    if not hasattr(request.user, "employeeprofile"):
        return redirect("login")

    employee = request.user.employeeprofile
    tasks = Task.objects.filter(employee=employee)

    completed_tasks = tasks.filter(status="completed").count()
    pending_tasks = tasks.exclude(status="completed").count()

    return render(request, "dashboard.html", {
        "tasks": tasks,
        "total": tasks.count(),
        "pending": pending_tasks,
        "completed": completed_tasks,
    })


# =========================
# EMPLOYEE TASK LIST
# =========================
@login_required
def task_list(request):
    if not hasattr(request.user, "employeeprofile"):
        return redirect("login")

    employee = request.user.employeeprofile
    tasks = Task.objects.filter(employee=employee)

    return render(request, "task_list.html", {"tasks": tasks})


# =========================
# EMPLOYEE TASK UPDATE
# =========================
@login_required
def task_update(request, task_id):
    if not hasattr(request.user, "employeeprofile"):
        return redirect("login")

    task = get_object_or_404(
        Task,
        id=task_id,
        employee=request.user.employeeprofile
    )

    if request.method == "POST":
        task.status = request.POST.get("status")
        task.save()
        messages.success(request, "Task updated successfully")
        return redirect("dashboard")

    return render(request, "task_update.html", {"task": task})


# =========================
# MANAGER DASHBOARD
# =========================
@login_required
def manager_dashboard(request):
    if not hasattr(request.user, "managerprofile"):
        return redirect("login")

    manager = request.user.managerprofile
    tasks = Task.objects.filter(manager=manager)

    completed_tasks = tasks.filter(status="completed").count()
    pending_tasks = tasks.exclude(status="completed").count()

    return render(request, "manager_dashboard.html", {
        "tasks": tasks,
        "employees_count": manager.employees.count(),
        "total": tasks.count(),
        "pending": pending_tasks,
        "completed": completed_tasks,
    })


# =========================
# MANAGER CREATE TASK
# =========================
@login_required
def create_task(request):
    if not hasattr(request.user, "managerprofile"):
        return redirect("login")

    manager = request.user.managerprofile

    if request.method == "POST":
        form = TaskCreateForm(request.POST, manager=manager)
        if form.is_valid():
            task = form.save(commit=False)
            task.manager = manager
            task.save()
            messages.success(request, "Task created successfully")
            return redirect("manager_dashboard")
    else:
        form = TaskCreateForm(manager=manager)

    return render(request, "create_task.html", {"form": form})


# =========================
# MANAGER DELETE TASK
# =========================
@staff_member_required
def delete_task(request, task_id):
    task = get_object_or_404(
        Task,
        id=task_id,
        manager=request.user.managerprofile
    )
    if task.status == 'completed':
        task.delete()
    return redirect('manager_dashboard')

