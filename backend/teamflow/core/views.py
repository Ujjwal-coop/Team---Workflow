from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect

from .models import Task, ManagerProfile, EmployeeProfile
from .forms import LoginForm, SignUpForm, TaskCreateForm


# ---------------- LOGIN ----------------
@csrf_protect
def login_view(request):
    form = LoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        role = form.cleaned_data["role"]

        user = authenticate(request, username=username, password=password)
        if not user:
            return render(request, "login.html", {"form": form, "error": "Invalid credentials"})

        # ADMIN / MANAGER
        if role == "admin":
            if user.is_superuser or ManagerProfile.objects.filter(user=user).exists():
                login(request, user)
                if user.is_superuser:
                    return redirect("admin_dashboard")
                return redirect("manager_dashboard")
            return render(request, "login.html", {"form": form, "error": "Not admin/manager"})

        # EMPLOYEE
        if role == "employee":
            if EmployeeProfile.objects.filter(user=user).exists():
                login(request, user)
                return redirect("dashboard")
            return render(request, "login.html", {"form": form, "error": "Not employee"})

    return render(request, "login.html", {"form": form})


# ---------------- SIGNUP ----------------
@csrf_protect
def signup_view(request):
    form = SignUpForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        EmployeeProfile.objects.create(user=user)
        return redirect("login")

    return render(request, "signup.html", {"form": form})


# ---------------- LOGOUT ----------------
def logout_view(request):
    logout(request)
    return redirect("login")


# ---------------- EMPLOYEE DASHBOARD ----------------
@login_required
def dashboard(request):
    employee = get_object_or_404(EmployeeProfile, user=request.user)
    tasks = Task.objects.filter(employee=employee)

    return render(request, "dashboard.html", {
        "tasks": tasks,
        "total": tasks.count(),
        "pending": tasks.filter(status="pending").count(),
        "completed": tasks.filter(status="completed").count(),
    })


# ---------------- MANAGER DASHBOARD ----------------
@login_required
def manager_dashboard(request):
    if not (request.user.is_superuser or ManagerProfile.objects.filter(user=request.user).exists()):
        return redirect("login")

    tasks = Task.objects.all()

    return render(request, "manager_dashboard.html", {
        "tasks": tasks,
        "employees_count": EmployeeProfile.objects.count(),
        "total": tasks.count(),
        "pending": tasks.filter(status="pending").count(),
        "completed": tasks.filter(status="completed").count(),
    })


# ---------------- CREATE TASK ----------------
@login_required
@csrf_protect
def create_task(request):
    if not (request.user.is_superuser or ManagerProfile.objects.filter(user=request.user).exists()):
        return redirect("login")

    form = TaskCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("manager_dashboard")

    return render(request, "create_task.html", {"form": form})


# ---------------- DELETE TASK ----------------
@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if not (request.user.is_superuser or ManagerProfile.objects.filter(user=request.user).exists()):
        return redirect("login")

    if task.status == "completed":
        task.delete()

    return redirect("manager_dashboard")


# ---------------- ADMIN DASHBOARD ----------------
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    return render(request, "admin_dashboard.html", {
        "users": User.objects.count(),
        "managers": ManagerProfile.objects.count(),
        "employees": EmployeeProfile.objects.count(),
        "tasks": Task.objects.count(),
    })
