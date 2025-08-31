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

            # 5. Add artist to claimed_artists
            lead.claimed_artists.add(artist_profile)
            lead.save()

            return Response({
                "message": "Lead claimed successfully.",
                "lead_id": lead.id,
                "claimed_count": lead.claimed_artists.count(),
                "max_claims": lead.max_claims,
                "created_at": lead.created_at,
                "updated_at": lead.updated_at
            }, status=200)
