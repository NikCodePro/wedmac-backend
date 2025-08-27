from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from artists.models.models import ArtistProfile
from artists.serializers.website.artist_card_serializers import ArtistCardSerializer
from adminpanel.models import MakeupType, Product
from django.db.models import Q

class ArtistCardListView(APIView):
    def post(self, request):
        data = request.data
        page = data.get("page", 1)
        page_size = data.get("page_size", 20)
        search_keyword = data.get("search_keyword", "").strip()
        filters = data.get("filters", {})
        queryset = ArtistProfile.objects.filter(status="approved")

        # Search by full name
        if search_keyword:
            queryset = queryset.filter(
                Q(first_name__icontains=search_keyword) |
                Q(last_name__icontains=search_keyword)
            )

        # Filter: Makeup Type (many-to-many)
        makeup_type = filters.get("makeuptype")
        if makeup_type:
            queryset = queryset.filter(type_of_makeup__name__icontains=makeup_type)

        # Filter: State & City
        if filters.get("state"):
            queryset = queryset.filter(location__state__iexact=filters["state"])
        if filters.get("city"):
            queryset = queryset.filter(location__city__iexact=filters["city"])

        # Filter: Ratings
        if filters.get("ratings"):
            queryset = queryset.filter(average_rating__gte=filters["ratings"])

        # Filter: Products Used (many-to-many)
        if filters.get("products"):
            queryset = queryset.filter(products_used__name__icontains=filters["products"])

        # Remove duplicates caused by many-to-many joins
        queryset = queryset.distinct().order_by("-average_rating")

        # Pagination
        start = (page - 1) * page_size
        end = start + page_size
        total_count = queryset.count()
        paginated_queryset = queryset[start:end]

        serializer = ArtistCardSerializer(paginated_queryset, many=True)
        return Response({
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "results": serializer.data
        }, status=status.HTTP_200_OK)
