from rest_framework.views import APIView
from rest_framework.response import Response
from superadmin_auth.permissions import IsSuperAdmin
from leads.models.selected_artist import SelectedArtist
from leads.serializers.selected_artist_serializer import SelectedArtistSerializer

class SelectedArtistView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        """List all selected artists"""
        selected_artists = SelectedArtist.objects.all()
        serializer = SelectedArtistSerializer(selected_artists, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Add a new artist to selected list"""
        serializer = SelectedArtistSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def delete(self, request):
        """Remove an artist from selected list"""
        artist_id = request.data.get('artist_id')
        try:
            selected_artist = SelectedArtist.objects.get(artist_id=artist_id)
            selected_artist.delete()
            return Response({"message": "Artist removed from selected list"}, status=200)
        except SelectedArtist.DoesNotExist:
            return Response({"error": "Artist not found in selected list"}, status=404)