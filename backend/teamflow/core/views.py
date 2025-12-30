from django.shortcuts import render

def login_view(request):
    return render(request, 'login.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def manager_dashboard(request):
    return render(request, 'manager_dashboard.html')

def task_list(request):
    return render(request, 'task_list.html')
