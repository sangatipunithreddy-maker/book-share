from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student','student'),
        ('faculty','faculty'),
        ('admin','admin'),
    )
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    year = models.CharField(max_length=20, blank=True, null=True)
    branch = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f'{self.username} ({self.email})'

class Timestamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class Ad(Timestamped):
    STATUS_CHOICES = (('Available','Available'),('Reserved','Reserved'),('Sold','Sold'))
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ads')

    def __str__(self):
        return f'{self.title} (₹{self.price})'

class Material(Timestamped):
    subject = models.CharField(max_length=120)
    semester = models.CharField(max_length=40, blank=True, null=True)
    academic_year = models.CharField(max_length=40, blank=True, null=True)
    filename = models.CharField(max_length=255)  # stored name; file storage can be added later
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='materials')
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.subject} - {self.filename}'

class InterviewPost(Timestamped):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interview_posts')

    def __str__(self):
        return self.title

class Notification(Timestamped):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    content = models.CharField(max_length=300)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f'Notif to {self.user_id}: {self.content[:30]}'

class ReportedAd(Timestamped):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    reason = models.CharField(max_length=200)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f'Report #{self.id} on Ad {self.ad_id}'
