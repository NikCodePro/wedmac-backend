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
        """Get the current tags for a specific artist"""
        try:
            artist = ArtistProfile.objects.get(id=artist_id)
            return Response({
                'artist_id': artist.id,
                'artist_name': f"{artist.first_name} {artist.last_name}",
                'tags': artist.tag or []
            }, status=status.HTTP_200_OK)
        except ArtistProfile.DoesNotExist:
            return Response({
                'error': 'Artist not found'
            }, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, artist_id):
        """Update the tags for a specific artist"""
        try:
            artist = ArtistProfile.objects.get(id=artist_id)
            tags = request.data.get('tags', [])

            # Validate tags
            if not isinstance(tags, list):
                return Response({
                    'error': 'Tags must be a list of strings'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Limit to 10 tags maximum
            if len(tags) > 10:
                return Response({
                    'error': 'Maximum 10 tags allowed per artist'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Filter out empty strings and duplicates
            tags = list(set(tag.strip() for tag in tags if tag.strip()))

            # Update the tags
            artist.tag = tags
            artist.save()

            return Response({
                'message': f'{len(tags)} tags updated successfully',
                'artist_id': artist.id,
                'artist_name': f"{artist.first_name} {artist.last_name}",
                'tags': artist.tag
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
                'tags': artist.tag or [],
                'status': artist.status,
                'created_at': artist.created_at
            })

        return Response(data, status=status.HTTP_200_OK)
