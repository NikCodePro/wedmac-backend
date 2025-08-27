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

            # 2. Check available leads
            if artist_profile.available_leads <= 0:
                return Response({
                    "error": "No leads available. Please purchase more leads.",
                    "available_leads": 0
                }, status=403)

            # 3. Get the lead
            try:
                lead = Lead.objects.select_for_update().get(id=lead_id, is_deleted=False)
            except Lead.DoesNotExist:
                return Response({"error": "Lead not found."}, status=404)

            # 4. Check if already assigned
            if lead.assigned_to:
                return Response({"error": "Lead already claimed by another artist."}, status=400)

            # 5. Deduct one lead from available_leads
            artist_profile.available_leads -= 1
            artist_profile.save()

            # 6. Assign lead to artist
            lead.assigned_to = artist_profile
            lead.status = 'claimed'  # Changed from 'contacted' to 'claimed'
            lead.save()

            return Response({
                "message": "Lead claimed successfully.",
                "lead_id": lead.id,
                "status": lead.status,
                "available_leads": artist_profile.available_leads,
                "created_at": lead.created_at,
                "updated_at": lead.updated_at
            }, status=200)
