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

                # Check if plan has expired
                if subscription.end_date and now > subscription.end_date:
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
                        available_leads_before_expiry=artist.available_leads,
                        plan_details=plan_snapshot
                    )

                    # Clear only the available leads, keep the current plan
                    artist.available_leads = 0
                    artist.plan_purchase_date = None
                    artist.plan_verified = False
                    artist.save()

                    # Deactivate the subscription
                    subscription.is_active = False
                    subscription.save()

                    logger.info(
                        f"Plan expired for artist {artist.first_name} {artist.last_name} "
                        f"(ID: {artist.id}). Leads before expiry: {artist.available_leads}. "
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
