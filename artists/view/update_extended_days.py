from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from artists.models.models import ArtistProfile

class UpdateExtendedDaysView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        artist_id = request.data.get('artist_id')
        delta = request.data.get('delta')

        if artist_id is None or delta is None:
            return Response({"error": "artist_id and delta are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            delta = int(delta)
        except ValueError:
            return Response({"error": "delta must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            artist = ArtistProfile.objects.get(id=artist_id)
        except ArtistProfile.DoesNotExist:
            return Response({"error": "Artist not found."}, status=status.HTTP_404_NOT_FOUND)

        new_value = artist.extended_days or 0
        new_value += delta
        if new_value < 0:
            return Response({"error": "extended_days cannot be negative."}, status=status.HTTP_400_BAD_REQUEST)

        artist.extended_days = new_value
        artist.save(update_fields=['extended_days'])

        return Response({"message": "extended_days updated successfully.", "extended_days": artist.extended_days})
