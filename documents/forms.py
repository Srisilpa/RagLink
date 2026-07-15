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
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "department": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.TextInput(attrs={"class": "form-control"}),
            "version": forms.TextInput(attrs={"class": "form-control"}),
            "file": forms.FileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["department"].required = False
        self.fields["category"].required = False
        self.fields["version"].required = False