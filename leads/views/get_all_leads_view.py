from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from leads.models.models import Lead
from leads.serializers.serializers import LeadSerializer
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class GetAllLeadsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit_param = request.query_params.get('limit', None)

        user = request.user
        artist_profile = None
        excluded_lead_ids = []

        # Get artist profile with better error handling
        try:
            if hasattr(user, 'artist_profile'):
                artist_profile = user.artist_profile
                logger.info(f"User {user.id} has artist profile: {artist_profile.id if artist_profile else None}")
            else:
                logger.info(f"User {user.id} does not have artist_profile attribute")
        except Exception as e:
            logger.error(f"Error accessing artist profile for user {user.id}: {str(e)}")

        # Start with all non-deleted leads
        leads = Lead.objects.filter(is_deleted=False).order_by('-created_at')

        # Filter out leads that are booked (have booked_artists) and leads older than 1 month
        one_month_ago = timezone.now() - timedelta(days=30)
        leads = leads.exclude(booked_artists__isnull=False).filter(created_at__gte=one_month_ago)

        # Exclude leads that have reached max claims
        from django.db.models import Count
        from django.db import models
        leads = leads.annotate(
            claimed_count=Count('claimed_artists')
        ).exclude(
            claimed_count__gte=models.F('max_claims')
        )

        # Filter out claimed leads based on artist profile
        if artist_profile:
            # Get leads claimed by this artist
            claimed_leads = leads.filter(claimed_artists=artist_profile)
            excluded_lead_ids.extend(claimed_leads.values_list('id', flat=True))

            # Exclude claimed leads
            leads = leads.exclude(claimed_artists=artist_profile)
            logger.info(f"Excluded {claimed_leads.count()} leads claimed by artist profile {artist_profile.id}")
        else:
            # If user doesn't have artist profile, exclude leads where user is the requested_artist
            requested_leads = leads.filter(requested_artist__user=user)
            excluded_lead_ids.extend(requested_leads.values_list('id', flat=True))
            leads = leads.exclude(requested_artist__user=user)
            logger.info(f"Excluded {requested_leads.count()} leads where user {user.id} is the requested_artist")

        # Additional safety check: also exclude leads where user is assigned_to
        if artist_profile:
            assigned_leads = leads.filter(assigned_to=artist_profile)
            excluded_lead_ids.extend(assigned_leads.values_list('id', flat=True))
            leads = leads.exclude(assigned_to=artist_profile)
            logger.info(f"Excluded {assigned_leads.count()} leads assigned to artist profile {artist_profile.id}")

        # Apply limit if specified
        if limit_param:
            try:
                limit = int(limit_param)
                if limit > 0:
                    leads = leads[:limit]
            except ValueError:
                return Response({"error": "Invalid limit parameter. Must be a positive integer."}, status=400)

        serializer = LeadSerializer(leads, many=True)
        leads_data = serializer.data

        # Add claimed_count and booked_count to each lead in response
        for i, lead in enumerate(leads):
            leads_data[i]['claimed_count'] = lead.claimed_artists.count()
            leads_data[i]['booked_count'] = lead.booked_artists.count()

        logger.info(f"User {user.id} - Total leads found: {len(leads_data)}, Excluded lead IDs: {excluded_lead_ids}")

        return Response({
            "message": "Fetched all leads successfully.",
            "count": leads.count(),
            "leads": leads_data,
            "debug_info": {
                "user_id": user.id,
                "has_artist_profile": artist_profile is not None,
                "artist_profile_id": artist_profile.id if artist_profile else None,
                "excluded_lead_ids": excluded_lead_ids,
                "total_excluded": len(excluded_lead_ids)
            }
        }, status=200)
