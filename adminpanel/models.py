import uuid
from django.db import models

class SubscriptionPlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    total_leads = models.IntegerField()
    total_credit_points = models.IntegerField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    features = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subscription_plans'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.price}"

    def save(self, *args, **kwargs):
        if not isinstance(self.id, uuid.UUID):
            try:
                self.id = uuid.UUID(str(self.id))
            except (ValueError, AttributeError):
                self.id = uuid.uuid4()
        super().save(*args, **kwargs)


class Service(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    credits = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - ₹{self.price} ({self.credits} credits)"
    


class BudgetRange(models.Model):
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=100, unique=True)  # e.g., "Below ₹5,000", "₹5,000 - ₹10,000"
    min_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        if self.min_value and self.max_value:
            return f"₹{self.min_value:.0f} - ₹{self.max_value:.0f}"
        return self.label


class MakeupType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)  # e.g., "HD", "Airbrush", "Matte", etc.
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)  # e.g., "Foundation", "Lipstick", etc.
    brand = models.CharField(max_length=100, blank=True, null=True)  # Optional brand field
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
    
class PaymentMethod(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)  # e.g., "Credit Card", "PayPal", etc.
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

