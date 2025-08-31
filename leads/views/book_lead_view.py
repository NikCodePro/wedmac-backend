# leads/views/book_lead_view.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction
from artists.models import ArtistProfile
from leads.models.models import Lead

class BookLeadView(APIView):
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

            # 4. Check if artist has claimed this lead
            if not lead.claimed_artists.filter(id=artist_profile.id).exists():
                return Response({"error": "You must claim this lead before booking it."}, status=400)

            # 5. Check if already booked by this artist
            if lead.booked_artists.filter(id=artist_profile.id).exists():
                return Response({"error": "You have already booked this lead."}, status=400)

            # 6. Deduct one lead from available_leads
            artist_profile.available_leads -= 1
            artist_profile.save()

            # 7. Add to booked_artists and set status to 'booked'
            lead.booked_artists.add(artist_profile)
            lead.status = 'booked'
            lead.save()

            return Response({
                "message": "Lead booked successfully.",
                "lead_id": lead.id,
                "status": lead.status,
                "available_leads": artist_profile.available_leads,
                "booked_count": lead.booked_artists.count(),
                "created_at": lead.created_at,
                "updated_at": lead.updated_at
            }, status=200)
