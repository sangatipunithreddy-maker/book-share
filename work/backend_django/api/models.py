from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student','student'),
        ('faculty','faculty'),
        ('admin','admin'),
    )
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default='student')
    year = models.CharField(max_length=16, blank=True, default='')
    branch = models.CharField(max_length=64, blank=True, default='')

    def __str__(self):
        return f"{self.username} ({self.role})"

class Ad(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ads')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Material(models.Model):
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='materials')
    name = models.CharField(max_length=200)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class InterviewPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interview_posts')
    title = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class ReportedAd(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    reason = models.CharField(max_length=255, blank=True)
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
