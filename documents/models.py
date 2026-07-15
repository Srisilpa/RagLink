from django.db import models
from django.conf import settings


def document_upload_path(instance, filename):
    return f"Projects/{filename}"


class Document(models.Model):

    title = models.CharField(max_length=200)

    department = models.CharField(
        max_length=100,
        blank=True
    )

    category = models.CharField(
        max_length=100,
        blank=True
    )

    version = models.CharField(
        max_length=20,
        blank=True
    )

    file = models.FileField(
        upload_to=document_upload_path
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title