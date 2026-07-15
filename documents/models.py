from django.db import models
from accounts.models import User


def document_upload_path(instance, filename):
    if instance.uploaded_by.role == "ADMIN":
        return f"Company/{filename}"
    elif instance.uploaded_by.role == "TEAM_LEAD":
        return f"Projects/{filename}"
    return f"documents/{filename}"


class Document(models.Model):
    title = models.CharField(max_length=255)
    department = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    version = models.CharField(max_length=20)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True)

    file = models.FileField(upload_to=document_upload_path)