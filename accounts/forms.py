from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "department",
            "password1",
            "password2",
        ]