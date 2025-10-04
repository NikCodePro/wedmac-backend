# leads/views/claim_lead_view.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from artists.models import ArtistProfile
from artists.models.models import ArtistSubscription
from leads.models.models import Lead

class ClaimLeadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, lead_id):
        with transaction.atomic():  # Use transaction for data consistency
            # 1. Get artist profile
            try:
                artist_profile = request.user.artist_profile
            except ArtistProfile.DoesNotExist:
                return Response({"error": "Artist profile not found."}, status=404)

            # 2. Get the lead
            try:
                lead = Lead.objects.select_for_update().get(id=lead_id, is_deleted=False)
            except Lead.DoesNotExist:
                return Response({"error": "Lead not found."}, status=404)

            # 3. Check if artist already claimed this lead
            if lead.claimed_artists.filter(id=artist_profile.id).exists():
                return Response({"error": "You have already claimed this lead."}, status=400)

            # 4. Check if max claims reached
            if lead.claimed_artists.count() >= lead.max_claims:
                return Response({"error": "Maximum claims reached for this lead."}, status=400)

            # 5. Check available leads
            if artist_profile.available_leads <= 0:
                return Response({
                    "error": "No leads available. Please purchase more leads.",
                    "available_leads": 0
                }, status=403)

            # 6. Deduct one lead from available_leads
            leads_before = int(artist_profile.available_leads or 0)
            artist_profile.available_leads -= 1
            artist_profile.save()
            leads_after = int(artist_profile.available_leads or 0)

            # Log the lead claim activity
            from artists.models.models import ArtistActivityLog
            ArtistActivityLog.objects.create(
                artist=artist_profile,
                activity_type='claim',
                leads_before=leads_before,
                leads_after=leads_after,
                details={
                    'lead_id': lead.id,
                    'lead_status': lead.status,
                }
            )

            # 7. Add artist to claimed_artists and update status
            lead.claimed_artists.add(artist_profile)
            lead.status = 'claimed'  # Update status to claimed
            lead.save()

            return Response({
                "message": "Lead claimed successfully.",
                "lead_id": lead.id,
                "claimed_count": lead.claimed_artists.count(),
                "max_claims": lead.max_claims,
                "status": lead.status,
                "created_at": lead.created_at,
                "updated_at": lead.updated_at
            }, status=200)
