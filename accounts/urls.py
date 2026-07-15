from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/admin/", views.admin_login, name="admin_login"),
    path("login/teamlead/", views.teamlead_login, name="teamlead_login"),
    path("login/employee/", views.employee_login, name="employee_login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),

    path("users/", views.manage_users, name="manage_users"),
    path("users/add/", views.add_user, name="add_user"),

    path("users/edit/<int:user_id>/", views.edit_user, name="edit_user"),
    path("users/reset/<int:user_id>/", views.reset_password, name="reset_password"),
    path("users/delete/<int:user_id>/", views.delete_user, name="delete_user"),
]