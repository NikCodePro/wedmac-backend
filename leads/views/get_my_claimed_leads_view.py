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
            assigned_to=artist_profile,
            is_deleted=False
        ).order_by('-created_at')

        serializer = ClaimedLeadListSerializer(leads, many=True)
        return Response(serializer.data, status=200)
