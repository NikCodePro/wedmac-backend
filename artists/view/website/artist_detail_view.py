# artists/views/website/artist_detail_view.py

from rest_framework import generics
from artists.models.models import ArtistProfile
from artists.serializers.website.artist_public_detail_serializer import ArtistPublicDetailSerializer

class ArtistPublicDetailView(generics.RetrieveAPIView):
    queryset = ArtistProfile.objects.filter(status='approved')
    serializer_class = ArtistPublicDetailSerializer
    lookup_field = 'id'
