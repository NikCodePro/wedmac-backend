from django.db import models
from users.models import User
from documents.models import Document
from django.utils.crypto import get_random_string

class Location(models.Model):
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10,blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.city}, {self.state} - {self.pincode}"


class ArtistProfile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="artist_profile")

    # Personal Info
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15,unique=True)
    email = models.EmailField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    # Location Info
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='artist_profiles')

    # Business Details
    referel_code = models.CharField(max_length=20, blank=True)
    my_referral_code = models.CharField(max_length=20, blank=True, null=True, unique=True)  # New field for referral code
    offer_chosen = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    type_of_makeup = models.ManyToManyField('adminpanel.MakeupType', related_name='artist_profiles', blank=True)
    price_range = models.CharField(max_length=100, blank=True)
    products_used = models.ManyToManyField('adminpanel.Product', related_name='artist_profiles', blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    payment_methods = models.ManyToManyField('adminpanel.PaymentMethod', related_name='artist_profiles', blank=True)
    services = models.JSONField(default=list, blank=True)
    travel_charges = models.TextField(default=False)
    travel_policy = models.TextField(blank=True)
    trial_available = models.BooleanField(default=False)
    trial_paid_type = models.CharField(
        max_length=10,
        choices=[('paid', 'Paid'), ('unpaid', 'Unpaid')],
        blank=True,
        null=True
    )
    tag = models.JSONField(default=list, blank=True, null=True)  # Field for multiple artist tags
    # Document References (latest active only)
    profile_picture = models.ForeignKey(
        Document, on_delete=models.SET_NULL, null=True, blank=True, related_name='artist_profile_picture'
    )
    certifications = models.ManyToManyField(Document, related_name='artist_certifications', blank=True)

    # History (multiple supporting/id docs)
    id_documents = models.ManyToManyField(Document, related_name='artist_id_documents', blank=True)
    supporting_images = models.ManyToManyField(Document, related_name='artist_supporting_images', blank=True)

    # Status Tracking
    payment_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('paid', 'Paid')],
        default='pending'
    )
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending'
    )
    internal_notes = models.TextField(blank=True)
    
    # ratings of the artist 
    average_rating = models.FloatField(default=0.0)
    total_ratings = models.PositiveIntegerField(default=0)

    # new: available leads for the artist
    available_leads = models.IntegerField(default=0)

    # new: active/inactive flag for admin control
    is_active = models.BooleanField(default=True)

    # new: current number of leads claimed by this artist (keeps in sync via Lead signals)
    my_claimed_leads = models.IntegerField(default=0)
    total_bookings = models.IntegerField(default=0)

    # new: extended days field
    extended_days = models.IntegerField(default=0, blank=True, null=True)

    # new: flag to identify if artist was created by admin
    created_by_admin = models.BooleanField(default=False)

    # new: current purchased plan information
    current_plan = models.ForeignKey('adminpanel.SubscriptionPlan', on_delete=models.SET_NULL, null=True, blank=True, related_name='current_artist_profiles')
    plan_purchase_date = models.DateTimeField(null=True, blank=True)
    retained_plan_date = models.DateTimeField(null=True, blank=True, help_text="Date when expired plan was retained/reactivated")
    plan_verified = models.BooleanField(default=False)

    # new: preferred locations (array of city names)
    preferred_locations = models.JSONField(default=list, blank=True, help_text="List of preferred city names")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user.phone})"
    
    # def generate_referral_code(self):
    #     """Generate unique referral code based on first name and random string"""
    #     if not self.my_referral_code:
    #         # Take first 6 characters of first name, convert to uppercase, remove spaces
    #         base_name = self.first_name.replace(' ', '').upper()[:6]
    #         # Add random 4-character alphanumeric string
    #         random_part = get_random_string(6, '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    #         self.my_referral_code = f"{base_name}{random_part}"
    #         self.save()
    #     return self.my_


PAYMENT_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('success', 'Success'),
    ('failed', 'Failed'),
]


class SocialLink(models.Model):
    artist = models.ForeignKey(
        'ArtistProfile',
        on_delete=models.CASCADE,
        related_name='social_links'
    )
    platform = models.CharField(max_length=50)
    url = models.URLField()

    class Meta:
        unique_together = ['artist', 'platform']

class ArtistActivityLog(models.Model):
    """Model to store logs of artist activities: purchase, claim, expiry, admin_update"""
    ACTIVITY_TYPES = [
        ('purchase', 'Plan Purchase'),
        ('claim', 'Lead Claim'),
        ('expiry', 'Plan Expiry'),
        ('admin_update', 'Admin Lead Update'),
    ]

    artist = models.ForeignKey('ArtistProfile', on_delete=models.CASCADE, related_name='activity_logs')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    leads_before = models.IntegerField()
    leads_after = models.IntegerField()
    details = models.JSONField(help_text="Additional details like plan info, lead id, etc.")

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Artist Activity Log'
        verbose_name_plural = 'Artist Activity Logs'

    def __str__(self):
        return f"{self.artist.first_name} {self.artist.last_name} - {self.activity_type} at {self.timestamp}"


class ExpiredPlanLog(models.Model):
    """Model to store logs of expired artist plans"""
    artist = models.ForeignKey('ArtistProfile', on_delete=models.CASCADE, related_name='expired_plan_logs')
    plan = models.ForeignKey('adminpanel.SubscriptionPlan', on_delete=models.CASCADE)
    plan_purchase_date = models.DateTimeField()
    plan_expiry_date = models.DateTimeField()
    available_leads_before_expiry = models.IntegerField()
    expired_at = models.DateTimeField(auto_now_add=True)
    plan_details = models.JSONField(help_text="Snapshot of plan details at expiry time")

    class Meta:
        ordering = ['-expired_at']
        verbose_name = 'Expired Plan Log'
        verbose_name_plural = 'Expired Plan Logs'

    def __str__(self):
        return f"{self.artist.first_name} {self.artist.last_name} - {self.plan.name} expired on {self.expired_at.date()}"


class ArtistSubscription(models.Model):
    artist = models.ForeignKey('artists.ArtistProfile', on_delete=models.CASCADE)
    plan = models.ForeignKey('adminpanel.SubscriptionPlan', on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)  # ✅ New
    total_leads_allocated = models.IntegerField(null=True, blank=True)  # ✅ New
    leads_used = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')  # ✅ New
    razorpay_order_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

# Add this method to your existing ArtistSubscription model
    def activate_subscription_and_create_credits(self):
        from credit_history.models import ArtistCreditBalance
        
        # Activate subscription
        self.is_active = True
        self.payment_status = 'success'
        self.save()
        
        # Update artist profile
        artist = self.artist
        artist.payment_status = 'paid'
        
        # Create or get credit balance
        credit_balance, created = ArtistCreditBalance.objects.get_or_create(artist=artist)
        
        # Add lead credits from subscription
        if self.plan.total_leads:
            credit_balance.add_lead_credits(
                amount=self.plan.total_leads,
                description=f"Subscription purchase: {self.plan.name}",
                reference_id=self.razorpay_order_id,
                subscription_plan=self.plan
            )
        
        artist.save()
        return credit_balance