from django.db import models

class UnresolvedQuery(models.Model):
    question = models.TextField()
    department = models.CharField(max_length=100)
    reason = models.TextField()
    resolved = models.BooleanField(default=False)