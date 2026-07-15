from django import forms
from .models import Document

class DocumentForm(forms.ModelForm):

    class Meta:
        model = Document

        fields = [
            "title",
            "department",
            "category",
            "version",
            "file",
        ]

        widgets = {

            "title": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "department": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "category": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "version": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "file": forms.FileInput(attrs={
                "class": "form-control"
            }),

        }