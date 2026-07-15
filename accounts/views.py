from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import User
from django.contrib import messages
from .forms import UserRegistrationForm, UserEditForm

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

            messages.success(
                request,
                "User added successfully."
            )

            return redirect("manage_users")

        else:

            messages.error(
                request,
                "Failed to create user."
            )

    else:

        form = UserRegistrationForm()

    return render(
        request,
        "admin/add_user.html",
        {
            "form": form
        }
    )

@login_required(login_url="home")
@login_required(login_url="home")
def edit_user(request, user_id):

    if request.user.role != "ADMIN":
        return redirect("dashboard")

    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":

        form = UserEditForm(
            request.POST,
            instance=user
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "User updated successfully."
            )

            return redirect("manage_users")

    else:

        form = UserEditForm(instance=user)

    return render(
        request,
        "admin/add_user.html",
        {
            "form": form
        }
    )


@login_required(login_url="home")
def reset_password(request, user_id):

    if request.user.role != "ADMIN":
        return redirect("dashboard")

    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":

        password = request.POST.get("password")

        user.set_password(password)

        user.save()

        messages.success(
            request,
            f"Password changed for {user.username}."
        )

        return redirect("manage_users")

    return render(
        request,
        "admin/reset_password.html",
        {
            "user": user
        }
    )


@login_required(login_url="home")
def delete_user(request, user_id):

    if request.user.role != "ADMIN":
        return redirect("dashboard")

    user = get_object_or_404(User, id=user_id)

    if user != request.user:

        username = user.username

        user.delete()

        messages.success(
            request,
            f"{username} deleted successfully."
        )

    else:

        messages.error(
            request,
            "You cannot delete your own account."
        )

    return redirect("manage_users")