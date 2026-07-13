from django.db import models
from accounts.models import User

class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class Feedback(models.Model):
    chat = models.ForeignKey(ChatHistory, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comments = models.TextField(blank=True)