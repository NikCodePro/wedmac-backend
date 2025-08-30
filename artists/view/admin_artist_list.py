# artists/views.py

from superadmin_auth.permissions import IsSuperAdmin
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from artists.models.models import ArtistProfile
from artists.serializers.serializers import AdminArtistProfileSerializer

class AdminArtistListView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        status_filter = request.query_params.get("status", None)
        qs = ArtistProfile.objects.all()
        
        # Only filter if a valid status is given
        valid = ["pending", "approved", "rejected"]
        if status_filter:
            status_filter = status_filter.lower()
            if status_filter not in valid + ["all"]:
                return Response(
                    {"error": "Invalid status filter."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if status_filter in valid:
                qs = qs.filter(status=status_filter)
            # if status_filter == "all", leave qs unfiltered

        qs = qs.order_by("-created_at")
        serializer = AdminArtistProfileSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
