from django.db import models
from django.conf import settings
from adminpanel.models import BudgetRange, MakeupType, Service
from artists.models import ArtistProfile, Location
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from artists.models.models import ArtistProfile

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
        ('booked', 'Booked'),
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
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES, null=True, blank=True)
    requirements = models.TextField(blank=True)
    booking_date = models.DateField()

    budget_range = models.ForeignKey(BudgetRange, on_delete=models.SET_NULL, null=True)
    makeup_types = models.ManyToManyField(MakeupType, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)

    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, null=True, blank=True)

    assigned_to = models.ForeignKey(
        ArtistProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_leads"
    )
    requested_artist = models.ForeignKey(
        ArtistProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="requested_leads"
    )

    max_claims = models.PositiveIntegerField(default=5)
    claimed_artists = models.ManyToManyField(ArtistProfile, blank=True, related_name="claimed_leads")
    booked_artists = models.ManyToManyField(ArtistProfile, blank=True, related_name="booked_leads")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    last_contact = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    total_bookings = models.IntegerField(default=0)
    total_claims = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.first_name or ''} {self.last_name or ''} - {self.phone or ''}"

# store previous assigned_to before save so we can update both old/new artists
@receiver(pre_save, sender='leads.Lead')
def _lead_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            prev = sender.objects.get(pk=instance.pk)
            instance._prev_assigned_to_id = getattr(prev, 'assigned_to_id', None)
        except sender.DoesNotExist:
            instance._prev_assigned_to_id = None
    else:
        instance._prev_assigned_to_id = None

@receiver(post_save, sender='leads.Lead')
def _lead_post_save(sender, instance, created, **kwargs):
    # Update my_claimed_leads count on ArtistProfile for claimed_artists
    for artist in instance.claimed_artists.all():
        try:
            count = sender.objects.filter(
                claimed_artists=artist, status='claimed', is_deleted=False
            ).count()
            if artist.my_claimed_leads != count:
                artist.my_claimed_leads = count
                artist.save(update_fields=['my_claimed_leads'])
        except ArtistProfile.DoesNotExist:
            continue

    # Update my_claimed_leads count for previous assigned_to if changed
    prev_id = getattr(instance, '_prev_assigned_to_id', None)
    curr_id = getattr(instance, 'assigned_to_id', None)
    for artist_id in {prev_id, curr_id}:
        if not artist_id:
            continue
        try:
            artist = ArtistProfile.objects.get(pk=artist_id)
            count = sender.objects.filter(
                assigned_to_id=artist_id, status='claimed', is_deleted=False
            ).count()
            if artist.my_claimed_leads != count:
                artist.my_claimed_leads = count
                artist.save(update_fields=['my_claimed_leads'])
        except ArtistProfile.DoesNotExist:
            continue

@receiver(post_delete, sender='leads.Lead')
def _lead_post_delete(sender, instance, **kwargs):
    # Update my_claimed_leads count on ArtistProfile for claimed_artists
    for artist in instance.claimed_artists.all():
        try:
            count = sender.objects.filter(
                claimed_artists=artist, status='claimed', is_deleted=False
            ).count()
            if artist.my_claimed_leads != count:
                artist.my_claimed_leads = count
                artist.save(update_fields=['my_claimed_leads'])
        except ArtistProfile.DoesNotExist:
            continue

    # Update my_claimed_leads count for assigned_to
    artist_id = getattr(instance, 'assigned_to_id', None)
    if not artist_id:
        return
    try:
        artist = ArtistProfile.objects.get(pk=artist_id)
        count = sender.objects.filter(
            assigned_to_id=artist_id, status='claimed', is_deleted=False
        ).count()
        if artist.my_claimed_leads != count:
            artist.my_claimed_leads = count
            artist.save(update_fields=['my_claimed_leads'])
    except ArtistProfile.DoesNotExist:
        pass
