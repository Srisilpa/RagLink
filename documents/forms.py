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

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter document title"
                }
            ),

            "department": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter department"
                }
            ),

            "category": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter category"
                }
            ),

            "version": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: v1.0"
                }
            ),

            "file": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf,.docx,.txt"
                }
            ),
        }

    def __init__(
        self,
        *args,
        **kwargs
    ):

        super().__init__(
            *args,
            **kwargs
        )

        self.fields[
            "department"
        ].required = False

        self.fields[
            "category"
        ].required = False

        self.fields[
            "version"
        ].required = False


    def clean_file(self):

        file = self.cleaned_data.get(
            "file"
        )

        if not file:
            raise forms.ValidationError(
                "Please select a document."
            )

        allowed_extensions = [
            ".pdf",
            ".docx",
            ".txt"
        ]

        filename = file.name.lower()

        if not any(
            filename.endswith(extension)
            for extension in allowed_extensions
        ):

            raise forms.ValidationError(
                "Only PDF, DOCX and TXT files are allowed."
            )

        return file