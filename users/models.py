from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class OTPVerification(models.Model):
    phone = models.CharField(max_length=15)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)

    def is_expired(self):
        return (timezone.now() - self.created_at).seconds > 300  # 5 minutes


class User(AbstractUser):
    ROLE_CHOICES = (
        ('artist', 'Artist'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='artist')
    phone = models.CharField(max_length=15, unique=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['username']  # ✅ Do NOT override this again below

    otp_verified = models.BooleanField(default=False)
    is_artist_approved = models.BooleanField(default=False)

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True)
    location = models.ForeignKey('artists.Location', on_delete=models.SET_NULL, null=True, blank=True, related_name='users')

    def __str__(self):
        return f"{self.username} ({self.phone})"
