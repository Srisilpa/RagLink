from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout


def home(request):
    return render(request, "home/index.html")


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
            {"error": "Invalid Admin credentials."}
        )

    return render(request, "registration/admin_login.html")


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
            {"error": "Invalid Team Lead credentials."}
        )

    return render(request, "registration/teamlead_login.html")


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
            {"error": "Invalid Employee credentials."}
        )

    return render(request, "registration/employee_login.html")


def dashboard(request):

    if not request.user.is_authenticated:
        return redirect("home")

    if request.user.role == "ADMIN":
        return render(request, "admin/admin_dashboard.html")

    elif request.user.role == "TEAM_LEAD":
        return render(request, "teamlead/teamlead_dashboard.html")

    return render(request, "employee/employee_dashboard.html")


def logout_view(request):
    logout(request)
    return redirect("home")