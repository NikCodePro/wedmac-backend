# artists/views.py

from superadmin_auth.permissions import IsSuperAdmin
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.db import models
from artists.models.models import ArtistProfile
from artists.serializers.serializers import AdminArtistProfileSerializer

class AdminArtistListView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        status_filter = request.query_params.get("status", None)
        search_query = request.query_params.get("search", None)
        qs = ArtistProfile.objects.all()

        # Search functionality
        if search_query:
            qs = qs.filter(
                models.Q(first_name__icontains=search_query) |
                models.Q(last_name__icontains=search_query) |
                models.Q(phone__icontains=search_query)
            )

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

        # Pagination
        paginator = PageNumberPagination()
        paginator.page_size = 5
        paginated_qs = paginator.paginate_queryset(qs, request)
        serializer = AdminArtistProfileSerializer(paginated_qs, many=True)
        return paginator.get_paginated_response(serializer.data)
