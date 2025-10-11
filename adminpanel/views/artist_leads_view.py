from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from artists.models.models import ArtistProfile

class AdminUpdateArtistLeadsView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, artist_id):
        action = request.data.get('action')
        amount = request.data.get('amount')

        if action not in ['add', 'remove']:
            return Response({'error': 'Invalid action. Use "add" or "remove".'}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(amount, int) or amount <= 0:
            return Response({'error': 'Amount must be a positive integer.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            artist = ArtistProfile.objects.get(id=artist_id)
        except ArtistProfile.DoesNotExist:
            return Response({'error': 'Artist not found.'}, status=status.HTTP_404_NOT_FOUND)

        leads_before = artist.available_leads

        if action == 'add':
            artist.available_leads += amount
        else:  # remove
            if artist.available_leads < amount:
                return Response({'error': 'Cannot remove more leads than available.'}, status=status.HTTP_400_BAD_REQUEST)
            artist.available_leads -= amount

        artist.save()
        leads_after = artist.available_leads

        # Log the admin update activity
        from artists.models.models import ArtistActivityLog
        ArtistActivityLog.objects.create(
            artist=artist,
            activity_type='admin_update',
            leads_before=leads_before,
            leads_after=leads_after,
            details={
                'action': action,
                'amount': amount,
                'reason': 'Admin lead update - refund or exceptional case'
            }
        )

        return Response({'message': f'Available leads updated successfully.', 'available_leads': artist.available_leads}, status=status.HTTP_200_OK)
