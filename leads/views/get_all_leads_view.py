from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from leads.models.models import Lead
from leads.serializers.serializers import LeadSerializer
from django.utils import timezone
from datetime import timedelta

class GetAllLeadsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit_param = request.query_params.get('limit', None)

        leads = Lead.objects.filter(is_deleted=False).order_by('-created_at')

        # Filter out leads that are booked and leads older than 1 month
        one_month_ago = timezone.now() - timedelta(days=30)
        leads = leads.exclude(status='booked').filter(created_at__gte=one_month_ago)

        if limit_param:
            try:
                limit = int(limit_param)
                if limit > 0:
                    leads = leads[:limit]
            except ValueError:
                return Response({"error": "Invalid limit parameter. Must be a positive integer."}, status=400)

        serializer = LeadSerializer(leads, many=True)
        leads_data = serializer.data

        # Add claimed_count and booked_count to each lead in response
        for i, lead in enumerate(leads):
            leads_data[i]['claimed_count'] = lead.claimed_artists.count()
            leads_data[i]['booked_count'] = lead.booked_artists.count()

        return Response({
            "message": "Fetched all leads successfully.",
            "count": leads.count(),
            "leads": leads_data
        }, status=200)
