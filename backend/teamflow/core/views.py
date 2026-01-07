from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect

from .models import Task, ManagerProfile, EmployeeProfile
from .forms import LoginForm, SignUpForm, TaskCreateForm


# ======================================================
# LOGIN
# ======================================================
@csrf_protect
def login_view(request):
    form = LoginForm(request.POST or None)
    managers = ManagerProfile.objects.all()

    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        role = form.cleaned_data["role"]
        selected_manager = form.cleaned_data.get("manager")

        user = authenticate(request, username=username, password=password)
        if not user:
            return render(
                request,
                "login.html",
                {"form": form, "error": "Invalid credentials", "managers": managers},
            )

        # -------- ADMIN --------
        if role == "admin" and user.is_superuser:
            login(request, user)
            return redirect("admin_dashboard")

        # -------- MANAGER --------
        if role == "admin" and ManagerProfile.objects.filter(user=user).exists():
            login(request, user)
            return redirect("manager_dashboard")

        # -------- EMPLOYEE --------
         # ================= EMPLOYEE =================
        if role == "employee":
            try:
                employee = EmployeeProfile.objects.get(user=user)
            except EmployeeProfile.DoesNotExist:
                return render(
                    request,
                    "login.html",
                    {
                        "form": form,
                        "error": "You are not registered as an employee",
                        "managers": managers,
                    },
                )

            # 🔐 CRITICAL CHECK: Manager must match
            if not selected_manager:
                return render(
                    request,
                    "login.html",
                    {
                        "form": form,
                        "error": "Please select your manager",
                        "managers": managers,
                    },
                )

            if employee.manager.id != selected_manager.id:
                return render(
                    request,
                    "login.html",
                    {
                        "form": form,
                        "error": "Incorrect manager selected. Please select your correct manager.",
                        "managers": managers,
                    },
                )

            # ✅ Correct manager → allow login
            login(request, user)
            return redirect("dashboard")

        return render(
            request,
            "login.html",
            {
                "form": form,
                "error": "Unauthorized role",
                "managers": managers,
            },
        )

    return render(request, "login.html", {"form": form, "managers": managers})


# ======================================================
# SIGNUP
# ======================================================
@csrf_protect
def signup_view(request):
    form = SignUpForm(request.POST or None)
    managers = ManagerProfile.objects.all()

    if request.method == "POST" and form.is_valid():
        user = form.save()
        role = form.cleaned_data["role"]

        # -------- MANAGER SIGNUP --------
        if role == "manager":
            ManagerProfile.objects.create(
                user=user,
                company_name=user.username
            )

        # -------- EMPLOYEE SIGNUP --------
        else:
            manager = form.cleaned_data["manager"]
            EmployeeProfile.objects.create(
                user=user,
                manager=manager
            )

        return redirect("login")

    return render(request, "signup.html", {"form": form, "managers": managers})


# ======================================================
# LOGOUT
# ======================================================
@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


# ======================================================
# EMPLOYEE DASHBOARD
# ======================================================
@login_required
def dashboard(request):
    employee = get_object_or_404(EmployeeProfile, user=request.user)
    tasks = employee.tasks.all()

    return render(
        request,
        "dashboard.html",
        {
            "tasks": tasks,
            "total": tasks.count(),
            "pending": tasks.exclude(status="completed").count(),
            "completed": tasks.filter(status="completed").count(),
        },
    )


# ======================================================
# MANAGER DASHBOARD
# ======================================================
@login_required
def manager_dashboard(request):
    manager = get_object_or_404(ManagerProfile, user=request.user)
    tasks = manager.tasks.all()

    return render(
        request,
        "manager_dashboard.html",
        {
            "tasks": tasks,
            "employees_count": manager.employees.count(),
            "total": tasks.count(),
            "pending": tasks.exclude(status="completed").count(),
            "completed": tasks.filter(status="completed").count(),
        },
    )


# ======================================================
# CREATE TASK (MANAGER ONLY)
# ======================================================
@login_required
@csrf_protect
def create_task(request):
    manager = get_object_or_404(ManagerProfile, user=request.user)

    form = TaskCreateForm(request.POST or None, manager=manager)

    if request.method == "POST" and form.is_valid():
        task = form.save(commit=False)
        task.manager = manager
        task.save()
        return redirect("manager_dashboard")

    return render(request, "create_task.html", {"form": form})


# ======================================================
# TASK UPDATE (EMPLOYEE ONLY)  ✅ FIXED
# ======================================================
@login_required
def task_update(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    # Only employee can update their own task
    if not hasattr(request.user, "employee_profile"):
        return redirect("login")

    if task.employee.user != request.user:
        return redirect("dashboard")

    if request.method == "POST":
        task.status = request.POST.get("status")
        task.save()
        return redirect("dashboard")

    return render(request, "task_update.html", {"task": task})


# ======================================================
# DELETE TASK (MANAGER / ADMIN)
# ======================================================
@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    # Admin override
    if request.user.is_superuser:
        task.delete()
        return redirect("manager_dashboard")

    manager = get_object_or_404(ManagerProfile, user=request.user)

    if task.manager == manager and task.status == "completed":
        task.delete()

    return redirect("manager_dashboard")


# ======================================================
# ADMIN DASHBOARD
# ======================================================
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    return render(
        request,
        "admin_dashboard.html",
        {
            "users": User.objects.count(),
            "managers": ManagerProfile.objects.count(),
            "employees": EmployeeProfile.objects.count(),
            "tasks": Task.objects.count(),
        },
    )
