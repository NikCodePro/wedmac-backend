import logging
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from artists.models.models import ArtistProfile, ArtistSubscription, ExpiredPlanLog
from adminpanel.models import SubscriptionPlan

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Check for expired artist subscription plans and update profiles accordingly'

    def handle(self, *args, **options):
        now = timezone.now()
        expired_count = 0

        # Get all artists with active current plans
        artists_with_plans = ArtistProfile.objects.filter(
            current_plan__isnull=False,
            plan_verified=True
        ).select_related('current_plan')

        for artist in artists_with_plans:
            try:
                # Find the corresponding active subscription
                subscription = ArtistSubscription.objects.filter(
                    artist=artist,
                    plan=artist.current_plan,
                    is_active=True,
                    payment_status='success'
                ).order_by('-created_at').first()

                if not subscription:
                    # If no active subscription found, check if we should still expire based on plan_purchase_date
                    if artist.plan_purchase_date:
                        # Calculate expiry date based on plan status even without active subscription
                        if artist.plan_purchase_date is None and artist.retained_plan_date:
                            # Plan was retained by admin, expiry is retained_plan_date + extended_days
                            expiry_date = artist.retained_plan_date + timedelta(days=artist.extended_days or 0)
                        else:
                            # Normal plan: base is plan_purchase_date + plan.duration_days, extended by extended_days if any
                            expiry_date = artist.plan_purchase_date + timedelta(days=artist.current_plan.duration_days)
                            if artist.extended_days and artist.extended_days > 0:
                                expiry_date = expiry_date + timedelta(days=artist.extended_days)

                        # Check if plan has expired
                        if expiry_date and now > expiry_date:
                            # Create a dummy subscription object for logging purposes
                            class DummySubscription:
                                def __init__(self, plan, artist):
                                    self.plan = plan
                                    self.artist = artist
                                    self.id = None

                            subscription = DummySubscription(artist.current_plan, artist)
                            logger.warning(f"No active subscription found for artist {artist.id} with plan {artist.current_plan.id}, but expiring based on plan_purchase_date")
                        else:
                            logger.warning(f"No active subscription found for artist {artist.id} with plan {artist.current_plan.id}")
                            continue
                    else:
                        logger.warning(f"No active subscription found for artist {artist.id} with plan {artist.current_plan.id}")
                        continue

                # Calculate expiry date based on plan status
                if artist.plan_purchase_date is None and artist.retained_plan_date:
                    # Plan was retained by admin, expiry is retained_plan_date + extended_days
                    expiry_date = artist.retained_plan_date + timedelta(days=artist.extended_days or 0)
                else:
                    # Normal plan: base is plan_purchase_date + plan.duration_days, extended by extended_days if any
                    expiry_date = artist.plan_purchase_date + timedelta(days=subscription.plan.duration_days)
                    if artist.extended_days and artist.extended_days > 0:
                        expiry_date = expiry_date + timedelta(days=artist.extended_days)

                # Check if plan has expired
                if expiry_date and now > expiry_date:
                    
                    # Capture old leads before changing
                    old_leads = artist.available_leads
                    
                    # Log the expiry
                    plan_snapshot = {
                        'name': subscription.plan.name,
                        'total_leads': subscription.plan.total_leads,
                        'duration_days': subscription.plan.duration_days,
                        'price': str(subscription.plan.price),
                        'features': subscription.plan.features,
                    }

                    # Convert UUID fields to string for JSON serialization
                    plan_id_str = str(subscription.plan.id)
                    subscription_id_str = str(subscription.id) if subscription.id else None

                    ExpiredPlanLog.objects.create(
                        artist=artist,
                        plan=subscription.plan,
                        plan_purchase_date=artist.plan_purchase_date,
                        plan_expiry_date=expiry_date,
                        available_leads_before_expiry=old_leads,
                        plan_details=plan_snapshot
                    )

                    # Clear only the available leads, keep the current plan intact
                    leads_before = int(artist.available_leads or 0)
                    artist.available_leads = 0
                    artist.extended_days = 0  # Reset extended days as they were consumed
                    artist.plan_purchase_date = None  # Set to null to denote plan has expired

                    # If this was a retained plan and extended days expired, also clear retained date
                    if artist.retained_plan_date:
                        artist.retained_plan_date = None

                    artist.save()
                    leads_after = int(artist.available_leads or 0)

                    # Log the expiry activity
                    from artists.models.models import ArtistActivityLog
                    ArtistActivityLog.objects.create(
                        artist=artist,
                        activity_type='expiry',
                        leads_before=leads_before,
                        leads_after=leads_after,
                        details={
                            'plan_name': subscription.plan.name,
                            'plan_id': plan_id_str,
                            'subscription_id': subscription_id_str,
                            'expired_at': expiry_date.isoformat()
                        }
                    )

                    # Deactivate the subscription
                    subscription.is_active = False
                    subscription.save()

                    logger.info(
                        f"Plan expired for artist {artist.first_name} {artist.last_name} "
                        f"(ID: {artist.id}). Leads before expiry: {old_leads}. "
                        f"Plan: {subscription.plan.name}, Expiry: {expiry_date}"
                    )

                    expired_count += 1

            except Exception as e:
                logger.error(f"Error processing artist {artist.id}: {str(e)}")
                continue

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed expired plans. {expired_count} plans expired and updated.'
            )
        )

        if expired_count == 0:
            self.stdout.write(
                self.style.WARNING('No expired plans found.')
            )
