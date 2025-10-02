from django.db import models
from boards_app.models import Board
from django.contrib.auth.models import User


class Task(models.Model):
    STATUS_CHOICES = [
        ("to-do", "To Do"),
        ("in-progress", "In Progress"),
        ("review", "Review"),
        ("done", "Done"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="to-do")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="medium")
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tasks")
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_tasks")
    due_date = models.DateField()
    comments_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.title}({self.title})"
    


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
            return f"{self.author.fullname}: {self.content[:30]}"
