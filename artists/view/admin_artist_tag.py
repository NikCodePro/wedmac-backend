from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from superadmin_auth.permissions import IsSuperAdmin
from artists.models.models import ArtistProfile
from artists.serializers.serializers import ArtistProfileSerializer


class AdminArtistTagView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request, artist_id):
        """Get the current tag for a specific artist"""
        try:
            artist = ArtistProfile.objects.get(id=artist_id)
            return Response({
                'artist_id': artist.id,
                'artist_name': f"{artist.first_name} {artist.last_name}",
                'tag': artist.tag
            }, status=status.HTTP_200_OK)
        except ArtistProfile.DoesNotExist:
            return Response({
                'error': 'Artist not found'
            }, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, artist_id):
        """Update the tag for a specific artist"""
        try:
            artist = ArtistProfile.objects.get(id=artist_id)
            tag = request.data.get('tag', '')

            # Update the tag
            artist.tag = tag
            artist.save()

            return Response({
                'message': 'Tag updated successfully',
                'artist_id': artist.id,
                'artist_name': f"{artist.first_name} {artist.last_name}",
                'tag': artist.tag
            }, status=status.HTTP_200_OK)

        except ArtistProfile.DoesNotExist:
            return Response({
                'error': 'Artist not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class AdminArtistTagListView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        """Get all artists with their tags"""
        artists = ArtistProfile.objects.all().order_by('-created_at')
        data = []

        for artist in artists:
            data.append({
                'id': artist.id,
                'name': f"{artist.first_name} {artist.last_name}",
                'phone': artist.phone,
                'tag': artist.tag,
                'status': artist.status,
                'created_at': artist.created_at
            })

        return Response(data, status=status.HTTP_200_OK)
