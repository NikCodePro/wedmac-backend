from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.core.paginator import Paginator
from django.db.models import Q
from artists.models.models import ArtistActivityLog, ArtistProfile
from artists.serializers.serializers import ArtistActivityLogSerializer


class AdminArtistActivityLogsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, artist_id):
        # Check if user is admin (assuming admin has a flag or group)
        # For now, assume permission is handled by middleware or view
        # You may need to adjust based on your admin authentication

        try:
            artist = ArtistProfile.objects.get(id=artist_id)
        except ArtistProfile.DoesNotExist:
            return Response({"error": "Artist not found."}, status=404)

        # Get query parameters for filtering and pagination
        activity_type = request.query_params.get('activity_type', None)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 20)

        # Filter logs for the specified artist
        logs = ArtistActivityLog.objects.filter(artist=artist).order_by('-timestamp')

        # Apply filters
        if activity_type:
            logs = logs.filter(activity_type=activity_type)

        if start_date:
            logs = logs.filter(timestamp__date__gte=start_date)

        if end_date:
            logs = logs.filter(timestamp__date__lte=end_date)

        # Paginate
        paginator = Paginator(logs, page_size)
        try:
            page_obj = paginator.page(page)
        except:
            return Response({"error": "Invalid page number."}, status=400)

        serializer = ArtistActivityLogSerializer(page_obj, many=True)

        return Response({
            "artist_id": artist_id,
            "artist_name": f"{artist.first_name} {artist.last_name}",
            "logs": serializer.data,
            "total_count": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": int(page),
            "page_size": int(page_size)
        }, status=200)
