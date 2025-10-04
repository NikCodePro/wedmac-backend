import logging
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from artists.models.models import ArtistProfile

logger = logging.getLogger(__name__)

class UpdateExtendedDaysView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        artist_id = request.data.get('artist_id')
        delta_extended_days = request.data.get('delta_extended_days')
        delta_available_leads = request.data.get('delta_available_leads')

        if artist_id is None:
            return Response({"error": "artist_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        if delta_extended_days is None and delta_available_leads is None:
            return Response({"error": "At least one of delta_extended_days or delta_available_leads must be provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate deltas
        if delta_extended_days is not None:
            try:
                delta_extended_days = int(delta_extended_days)
            except ValueError:
                return Response({"error": "delta_extended_days must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        if delta_available_leads is not None:
            try:
                delta_available_leads = int(delta_available_leads)
            except ValueError:
                return Response({"error": "delta_available_leads must be an integer."}, status=status.HTTP_400_BAD_REQUEST)
            if delta_available_leads <= 0:
                return Response({"error": "delta_available_leads must be a positive integer."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            artist = ArtistProfile.objects.get(id=artist_id)
        except ArtistProfile.DoesNotExist:
            return Response({"error": "Artist not found."}, status=status.HTTP_404_NOT_FOUND)

        response_data = {"message": "Update successful."}

        # Update extended_days if provided
        if delta_extended_days is not None:
            old_value = artist.extended_days or 0
            new_value = old_value + delta_extended_days
            logger.info(f"Updating extended_days for artist {artist_id}: {old_value} + {delta_extended_days} = {new_value}")
            if new_value < 0:
                return Response({"error": "extended_days cannot be negative."}, status=status.HTTP_400_BAD_REQUEST)
            artist.extended_days = new_value
            response_data["extended_days"] = new_value

        # Update available_leads if provided
        if delta_available_leads is not None:
            leads_before = int(artist.available_leads or 0)
            new_value = leads_before + delta_available_leads
            logger.info(f"Updating available_leads for artist {artist_id}: {leads_before} + {delta_available_leads} = {new_value}")
            artist.available_leads = new_value
            response_data["available_leads"] = new_value

            # Log the admin lead addition activity
            from artists.models.models import ArtistActivityLog
            ArtistActivityLog.objects.create(
                artist=artist,
                activity_type='admin_add',
                leads_before=leads_before,
                leads_after=new_value,
                details={
                    'added_by_admin': True,
                    'leads_added': delta_available_leads,
                    'reason': 'Admin manual addition'
                }
            )
            logger.info(f"Activity log created for admin add")

        # Save the artist
        artist.save()
        logger.info(f"Artist {artist_id} updated successfully")

        return Response(response_data)
