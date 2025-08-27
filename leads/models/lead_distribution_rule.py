from django.db import models

class LeadDistributionRule(models.Model):
    STRATEGY_CHOICES = [
        ('round_robin', 'Round Robin'),
        ('capacity_based', 'Capacity Based'),
    ]
    strategy = models.CharField(max_length=30, choices=STRATEGY_CHOICES, unique=True)
    is_active = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.strategy} (Active: {self.is_active})"



class LeadDistributionConfig(models.Model):
    key = models.CharField(max_length=50, unique=True)
    value = models.TextField()

    def __str__(self):
        return f"{self.key} → {self.value}"
