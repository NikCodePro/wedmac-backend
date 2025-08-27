from django.db import models
from django.conf import settings
from adminpanel.models import BudgetRange, MakeupType, Service
from artists.models import ArtistProfile, Location

class Lead(models.Model):
    EVENT_CHOICES = [
        ('wedding', 'Wedding'),
        ('engagement', 'Engagement'),
        ('party', 'Party'),
        ('corporate', 'Corporate'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('new', 'New'),
        ('claimed', 'Claimed'),
        ('qualified', 'Qualified'),
        ('unqualified', 'Unqualified'),
        ('converted', 'Converted'),
    ]

    SOURCE_CHOICES = [
        ('website', 'Website'),
        ('instagram', 'Instagram'),
        ('referral', 'Referral'),
        ('other', 'Other'),
    ]

    # ✅ Newly added fields made safe for migration
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(blank=True, null=True)

    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True)
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES)
    requirements = models.TextField(blank=True)
    booking_date = models.DateField()

    budget_range = models.ForeignKey(BudgetRange, on_delete=models.SET_NULL, null=True)
    makeup_types = models.ManyToManyField(MakeupType, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)

    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, null=True, blank=True)

    assigned_to = models.ForeignKey(
        ArtistProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_leads"
    )
    requested_artist = models.ForeignKey(
        ArtistProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="requested_leads"
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    last_contact = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name or ''} {self.last_name or ''} - {self.phone or ''}"
