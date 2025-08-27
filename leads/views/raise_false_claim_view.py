# leads/views/raise_false_claim_view.py

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from leads.models.models import Lead
from leads.serializers.false_lead_claim_serializer import FalseLeadClaimSerializer

class RaiseFalseLeadClaimView(APIView):
    """
    Artist API: Raise a false lead claim
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            artist = request.user.artist_profile
        except:
            return Response({"error": "Only artists can raise false claims."}, status=403)

        serializer = FalseLeadClaimSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(artist=artist)
            return Response({
                "message": "False lead claim raised successfully.",
                "claim": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
