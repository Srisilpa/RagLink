from django.db import models
from accounts.models import User

class SearchLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.TextField()
    confidence = models.FloatField()
    time = models.DateTimeField(auto_now_add=True)