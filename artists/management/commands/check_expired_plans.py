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
                    logger.warning(f"No active subscription found for artist {artist.id} with plan {artist.current_plan.id}")
                    continue

                # Calculate effective end date considering extended days and retained plan date
                if artist.retained_plan_date and artist.extended_days and artist.extended_days > 0:
                    # If plan was retained and has extended days, calculate from retained date
                    effective_end_date = artist.retained_plan_date + timedelta(days=artist.extended_days)
                elif subscription.end_date and now > subscription.end_date:
                    # Plan expired, check if extended days exist
                    if artist.extended_days and artist.extended_days > 0:
                        # Use only extended days as effective end date from now
                        effective_end_date = subscription.end_date + timedelta(days=artist.extended_days)
                        if now > effective_end_date:
                            # Extended days also expired, proceed with expiry
                            pass
                        else:
                            # Plan is extended only by extended_days, skip expiry
                            logger.info(
                                f"Plan expired but extended days active for artist {artist.first_name} {artist.last_name} "
                                f"(ID: {artist.id}). Extended days: {artist.extended_days}. New expiry: {effective_end_date}"
                            )
                            continue
                    else:
                        # No extended days, plan expired
                        effective_end_date = subscription.end_date
                else:
                    effective_end_date = subscription.end_date

                # Check if plan has expired (considering extended days)
                if effective_end_date and now > effective_end_date:
                    
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

                    ExpiredPlanLog.objects.create(
                        artist=artist,
                        plan=subscription.plan,
                        plan_purchase_date=artist.plan_purchase_date,
                        plan_expiry_date=subscription.end_date,
                        available_leads_before_expiry=old_leads,
                        plan_details=plan_snapshot
                    )

                    # Clear only the available leads, keep the current plan intact
                    leads_before = int(artist.available_leads or 0)
                    artist.available_leads = 0
                    artist.extended_days = None  # Reset extended days as they were consumed
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
                            'plan_id': subscription.plan.id,
                            'subscription_id': subscription.id,
                            'expired_at': subscription.end_date.isoformat()
                        }
                    )

                    # Deactivate the subscription
                    subscription.is_active = False
                    subscription.save()

                    logger.info(
                        f"Plan expired for artist {artist.first_name} {artist.last_name} "
                        f"(ID: {artist.id}). Leads before expiry: {old_leads}. "
                        f"Plan: {subscription.plan.name}, Expiry: {subscription.end_date}"
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
