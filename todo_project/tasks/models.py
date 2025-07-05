from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # Поле first_name уже есть в AbstractUser, но ты делаешь его обязательным
    first_name = models.CharField(max_length=150, blank=False)

    # Удаляем метод save — валидация будет в сериализаторе


class Task(models.Model):
    STATUS_CHOICES = [
        ('New', 'New'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Pending', 'Pending'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
