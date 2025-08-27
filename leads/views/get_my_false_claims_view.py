# leads/views/get_my_false_claims_view.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from leads.models.false_lead_claim import FalseLeadClaim
from leads.serializers.false_lead_claim_serializer import FalseLeadClaimSerializer

class GetMyFalseClaimsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        artist = request.user.artist_profile
        status_filter = request.query_params.get('status')

        # Fetch according to status
        if status_filter in ['pending', 'approved', 'rejected']:
            claims = FalseLeadClaim.objects.filter(artist=artist, status=status_filter)
        else:
            # Fetch all if no specific or invalid status provided
            claims = FalseLeadClaim.objects.filter(artist=artist)

        serializer = FalseLeadClaimSerializer(claims, many=True)
        return Response(serializer.data)
