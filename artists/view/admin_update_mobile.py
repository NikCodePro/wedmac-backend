from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from artists.models.models import ArtistProfile
import re

class AdminUpdateMobileView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, artist_id):
        new_phone = request.data.get('phone')
        if not new_phone:
            return Response({"error": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate phone number
        if not self._is_valid_phone_number(new_phone):
            return Response({"error": "Invalid phone number format. Phone number should be 10-15 digits, optionally starting with '+'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            artist = ArtistProfile.objects.get(id=artist_id)
        except ArtistProfile.DoesNotExist:
            return Response({"error": "Artist not found."}, status=status.HTTP_404_NOT_FOUND)

        artist.phone = new_phone
        artist.save(update_fields=['phone'])

        return Response({
            "message": "Artist phone number updated successfully.",
            "artist_id": artist.id,
            "new_phone": artist.phone
        }, status=status.HTTP_200_OK)

    def _is_valid_phone_number(self, phone):
        """
        Validate phone number format.
        - Should be 10-15 digits
        - Can optionally start with '+'
        - No other characters allowed
        """
        # Remove spaces, hyphens, etc. for validation
        cleaned_phone = re.sub(r'[^\d+]', '', phone)

        # Check if it starts with + (optional) followed by digits
        if cleaned_phone.startswith('+'):
            digits = cleaned_phone[1:]
        else:
            digits = cleaned_phone

        # Check length (10-15 digits)
        if not 10 <= len(digits) <= 15:
            return False

        # Check if all characters are digits
        if not digits.isdigit():
            return False

        return True
