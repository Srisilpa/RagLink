from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .forms import UserRegistrationForm
from .models import User


# -------------------------
# Home Page
# -------------------------

def home(request):
    return render(request, "home/index.html")


# -------------------------
# Admin Login
# -------------------------

def admin_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user and user.role == "ADMIN":

            login(request, user)

            return redirect("dashboard")

        return render(
            request,
            "registration/admin_login.html",
            {
                "error": "Invalid Admin Credentials."
            }
        )

    return render(request, "registration/admin_login.html")


# -------------------------
# Team Lead Login
# -------------------------

def teamlead_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user and user.role == "TEAM_LEAD":

            login(request, user)

            return redirect("dashboard")

        return render(
            request,
            "registration/teamlead_login.html",
            {
                "error": "Invalid Team Lead Credentials."
            }
        )

    return render(request, "registration/teamlead_login.html")


# -------------------------
# Employee Login
# -------------------------

def employee_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user and user.role == "EMPLOYEE":

            login(request, user)

            return redirect("dashboard")

        return render(
            request,
            "registration/employee_login.html",
            {
                "error": "Invalid Employee Credentials."
            }
        )

    return render(request, "registration/employee_login.html")


# -------------------------
# Dashboard
# -------------------------

@login_required(login_url="home")
def dashboard(request):

    if request.user.role == "ADMIN":

        return render(
            request,
            "admin/dashboard.html"
        )

    elif request.user.role == "TEAM_LEAD":

        return render(
            request,
            "teamlead/teamlead_dashboard.html"
        )

    return render(
        request,
        "employee/employee_dashboard.html"
    )


# -------------------------
# Logout
# -------------------------

def logout_view(request):

    logout(request)

    return redirect("home")


# -------------------------
# Manage Users
# -------------------------

@login_required(login_url="home")
def manage_users(request):

    if request.user.role != "ADMIN":

        return redirect("dashboard")

    users = User.objects.all()

    search = request.GET.get("search", "")
    role = request.GET.get("role", "")
    department = request.GET.get("department", "")

    if search:

        users = users.filter(
            username__icontains=search
        )

    if role:

        users = users.filter(
            role=role
        )

    if department:

        users = users.filter(
            department__icontains=department
        )

    users = users.order_by(
        "role",
        "username"
    )

    context = {

        "users": users,

        "search": search,

        "role": role,

        "department": department,

    }

    return render(

        request,

        "admin/manage_users.html",

        context

    )


# -------------------------
# Add User
# -------------------------

@login_required(login_url="home")
def add_user(request):

    if request.user.role != "ADMIN":

        return redirect("dashboard")

    if request.method == "POST":

        form = UserRegistrationForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("manage_users")

    else:

        form = UserRegistrationForm()

    return render(

        request,

        "admin/add_user.html",

        {

            "form": form

        }

    )