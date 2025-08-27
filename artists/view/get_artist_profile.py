from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from artists.models.models import ArtistProfile
from artists.serializers.serializers import ArtistProfileSerializer
from documents.models import Document

class GetArtistProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            artist_profile = user.artist_profile
            serializer = ArtistProfileSerializer(artist_profile)
            data = serializer.data

            # add total available leads to response (support possible field names)
            leads = None
            for attr in ('available_leads', 'available_lead', 'total_available_leads'):
                val = getattr(artist_profile, attr, None)
                if val is not None:
                    try:
                        leads = int(val)
                    except Exception:
                        leads = 0
                    break
            if leads is None:
                leads = 0

            data['available_leads'] = leads
            return Response(data)
        except ArtistProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=404)
