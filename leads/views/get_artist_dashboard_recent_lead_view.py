from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.timezone import now, timedelta
from django.db.models.functions import Lower
from leads.models.models import Lead
from leads.serializers.serializers import LeadDashboardListSerializer

class ArtistRecentLeadsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        artist_profile = request.user.artist_profile  

        today = now().date()
        start_of_week = today - timedelta(days=today.weekday())  # Monday
        start_of_month = today.replace(day=1)

        # Get leads assigned to this artist, with specific status
        leads = Lead.objects.filter(
            # assigned_to=artist_profile,
            status__in=['new', 'claimed'],  # Changed from 'contacted' to 'claimed'
            is_deleted=False
        ).order_by('-created_at')

        # Count summaries
        new_this_week = leads.filter(created_at__date__gte=start_of_week, status='new').count()
        total_this_month = leads.filter(created_at__date__gte=start_of_month).count()

        serializer = LeadDashboardListSerializer(leads, many=True)

        return Response({
            "summary": {
                "new_this_week": new_this_week,
                "total_this_month": total_this_month
            },
            "leads": serializer.data
        })
