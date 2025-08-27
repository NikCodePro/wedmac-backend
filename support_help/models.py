from django.db import models
from django.conf import settings
from django.utils import timezone

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    CATEGORY_CHOICES = [
        ('account', 'Account Issues'),
        ('payment', 'Payment Issues'),
        ('technical', 'Technical Issues'),
        ('content', 'Content Related'),
        ('profile', 'Profile Related'),
        ('other', 'Other'),
    ]
    
    # Ticket details from artist
    subject = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    description = models.TextField()
    
    # System fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Relationships
    artist = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='tickets'
    )
    
    # Admin response fields
    admin_response = models.TextField(blank=True, null=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Support Ticket'
        verbose_name_plural = 'Support Tickets'
    
    def __str__(self):
        return f"{self.subject} - {self.artist.username}"
    
    def save(self, *args, **kwargs):
        # Set resolved_at when status changes to resolved
        if self.status == 'resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        super().save(*args, **kwargs)