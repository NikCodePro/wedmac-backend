# leads/views/get_my_claimed_leads_view.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from leads.models.models import Lead
from leads.serializers.serializers import ClaimedLeadListSerializer

class GetMyClaimedLeadsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            artist_profile = user.artist_profile
        except:
            return Response({"error": "Only artists can access their claimed leads."}, status=403)

        leads = Lead.objects.filter(
            claimed_artists=artist_profile,
            is_deleted=False
        ).order_by('-created_at')

        serializer = ClaimedLeadListSerializer(leads, many=True)
        leads_data = serializer.data

        # Add budget, makeup_types, assigned_count, claimed_count to each lead
        for i, lead in enumerate(leads):
            leads_data[i]['budget_range'] = lead.budget_range.label if lead.budget_range else None
            leads_data[i]['makeup_types'] = [mt.name for mt in lead.makeup_types.all()]
            leads_data[i]['assigned_count'] = lead.booked_artists.count()  # Artists who have booked this lead
            leads_data[i]['claimed_count'] = lead.claimed_artists.count()  # Artists who have claimed this lead

        return Response({
            "message": "Fetched claimed leads successfully.",
            "count": leads.count(),
            "leads": leads_data
        }, status=200)
