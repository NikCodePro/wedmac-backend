from django.db import models
from django.utils import timezone
from artists.models import ArtistProfile
from adminpanel.models import SubscriptionPlan

class CreditType(models.TextChoices):
    LEAD_CREDIT = 'lead_credit', 'Lead Credit'
    PREMIUM_FEATURE = 'premium_feature', 'Premium Feature'
    BOOST_PROFILE = 'boost_profile', 'Boost Profile'
    REFFERAL = 'referral', 'Referral'


class CreditTransaction(models.Model):
    """
    Track all credit transactions for artists
    """
    TRANSACTION_TYPES = [
        ('purchase', 'Purchase'),
        ('consumption', 'Consumption'),
        ('refund', 'Refund'),
        ('adjustment', 'Adjustment'),
        ('referral', 'Referral'),  # Add this new type
    ]
    
    artist = models.ForeignKey(
        ArtistProfile, 
        on_delete=models.CASCADE, 
        related_name='credit_transactions'
    )
    subscription_plan = models.ForeignKey(
        SubscriptionPlan, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='credit_transactions'
    )
    
    # Transaction details
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    credit_type = models.CharField(max_length=20, choices=CreditType.choices, default=CreditType.LEAD_CREDIT)
    
    # Credit amounts
    credits_before = models.IntegerField(default=0)
    credits_amount = models.IntegerField()  # Can be positive (add) or negative (deduct)
    credits_after = models.IntegerField(default=0)
    
    # Description and metadata
    description = models.TextField(blank=True)
    reference_id = models.CharField(max_length=100, blank=True)  # Order ID, booking ID, etc.
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['artist', 'created_at']),
            models.Index(fields=['transaction_type', 'credit_type']),
            models.Index(fields=['artist', 'transaction_type']),
        ]

    def __str__(self):
        return f"{self.artist.full_name} - {self.transaction_type} - {self.credits_amount}"

    @property
    def is_positive(self):
        return self.credits_amount > 0

    @property
    def is_negative(self):
        return self.credits_amount < 0

class ArtistCreditBalance(models.Model):
    """
    Current credit balance for each artist
    """
    artist = models.OneToOneField(
        ArtistProfile, 
        on_delete=models.CASCADE, 
        related_name='credit_balance'
    )
    
    # Current balances
    lead_credits = models.IntegerField(default=0)
    premium_feature_credits = models.IntegerField(default=0)
    boost_profile_credits = models.IntegerField(default=0)
    
    # Total lifetime credits earned
    total_lead_credits_earned = models.IntegerField(default=0)
    total_premium_credits_earned = models.IntegerField(default=0)
    total_boost_credits_earned = models.IntegerField(default=0)
    
    # Total credits consumed
    total_lead_credits_consumed = models.IntegerField(default=0)
    total_premium_credits_consumed = models.IntegerField(default=0)
    total_boost_credits_consumed = models.IntegerField(default=0)
    
    # Last updated
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Artist Credit Balance"
        verbose_name_plural = "Artist Credit Balances"

    def __str__(self):
        return f"{self.artist.full_name} - Lead Credits: {self.lead_credits}"

    def get_total_credits(self):
        return self.lead_credits + self.premium_feature_credits + self.boost_profile_credits

    def get_credit_summary(self):
        return {
            'lead_credits': self.lead_credits,
            'premium_feature_credits': self.premium_feature_credits,
            'boost_profile_credits': self.boost_profile_credits,
            'total_credits': self.get_total_credits(),
            'total_earned': {
                'lead_credits': self.total_lead_credits_earned,
                'premium_feature_credits': self.total_premium_credits_earned,
                'boost_profile_credits': self.total_boost_credits_earned,
            },
            'total_consumed': {
                'lead_credits': self.total_lead_credits_consumed,
                'premium_feature_credits': self.total_premium_credits_consumed,
                'boost_profile_credits': self.total_boost_credits_consumed,
            }
        }

    def add_lead_credits(self, amount, description="", reference_id="", subscription_plan=None):
        """Add lead credits to artist balance"""
        return self._create_transaction(
            credit_type=CreditType.LEAD_CREDIT,
            amount=amount,
            transaction_type='purchase',
            description=description,
            reference_id=reference_id,
            subscription_plan=subscription_plan
        )

    def consume_lead_credits(self, amount, description="", reference_id=""):
        """Consume lead credits from artist balance"""
        if self.lead_credits < amount:
            raise ValueError("Insufficient lead credits")
        
        return self._create_transaction(
            credit_type=CreditType.LEAD_CREDIT,
            amount=-amount,
            transaction_type='consumption',
            description=description,
            reference_id=reference_id
        )

    def _create_transaction(self, credit_type, amount, transaction_type, description="", reference_id="", subscription_plan=None):
        """Create a credit transaction and update balance"""
        # Get current balance based on credit type
        current_balance = getattr(self, f"{credit_type}_credits", 0)
        new_balance = current_balance + amount
        
        # Create transaction record
        transaction = CreditTransaction.objects.create(
            artist=self.artist,
            subscription_plan=subscription_plan,
            transaction_type=transaction_type,
            credit_type=credit_type,
            credits_before=current_balance,
            credits_amount=amount,
            credits_after=new_balance,
            description=description,
            reference_id=reference_id
        )
        
        # Update balance
        setattr(self, f"{credit_type}_credits", new_balance)
        
        # Update totals
        if amount > 0:
            total_earned_field = f"total_{credit_type}_credits_earned"
            setattr(self, total_earned_field, getattr(self, total_earned_field, 0) + amount)
        else:
            total_consumed_field = f"total_{credit_type}_credits_consumed"
            setattr(self, total_consumed_field, getattr(self, total_consumed_field, 0) + abs(amount))
        
        self.save()
        return transaction

# Signal to create credit balance when artist profile is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=ArtistProfile)
def create_artist_credit_balance(sender, instance, created, **kwargs):
    if created:
        ArtistCreditBalance.objects.create(artist=instance)