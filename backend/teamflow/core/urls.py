from django.urls import path
from . import views

urlpatterns = [
    # ================= AUTH =================
    path("", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),

    # ================= DASHBOARDS =================
    path("dashboard/", views.dashboard, name="dashboard"),          # Employee
    path("manager/", views.manager_dashboard, name="manager_dashboard"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),

    # ================= TASK MANAGEMENT =================
    path("create-task/", views.create_task, name="create_task"),    # Manager only
    path("task-update/<int:task_id>/", views.task_update, name="task_update"),
    path("delete-task/<int:task_id>/", views.delete_task, name="delete_task"),
]
