from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Role-based redirect
            if user.is_staff:
                return redirect('manager_dashboard')
            else:
                return redirect('dashboard')
        else:
            return render(request, 'login.html', {
                'error': 'Invalid username or password'
            })

    return render(request, 'login.html')


@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


@login_required
def manager_dashboard(request):
    return render(request, 'manager_dashboard.html')


@login_required
def task_list(request):
    return render(request, 'task_list.html')


def logout_view(request):
    logout(request)
    return redirect('login')
