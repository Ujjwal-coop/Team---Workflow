from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),

    path("dashboard/", views.dashboard, name="dashboard"),
    path("manager/", views.manager_dashboard, name="manager_dashboard"),

    path("create-task/", views.create_task, name="create_task"),
    path("delete-task/<int:task_id>/", views.delete_task, name="delete_task"),

    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
]
