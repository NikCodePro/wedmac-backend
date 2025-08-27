# leads/views/claim_detail_view.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from leads.models.false_lead_claim import FalseLeadClaim
from leads.serializers.false_lead_claim_serializer import FalseLeadClaimSerializer
from users.permissions import IsAdminRole  # or use your IsAdminUser alias

class ClaimDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request, claim_id):
        try:
            claim = FalseLeadClaim.objects.get(id=claim_id)
        except FalseLeadClaim.DoesNotExist:
            return Response({"error": "False lead claim not found."}, status=404)

        serializer = FalseLeadClaimSerializer(claim)
        return Response({"false_lead":serializer.data,"status":"success"},status=200)
