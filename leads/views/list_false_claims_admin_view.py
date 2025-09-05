from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from leads.models.false_lead_claim import FalseLeadClaim
from leads.serializers.false_lead_claim_serializer import FalseLeadClaimSerializer
from users.permissions import IsAdminRole  # ✅ Correct import
from superadmin_auth.permissions import IsSuperAdmin  # ✅ Correct import

class ListFalseClaimsAdminView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        status_filter = request.query_params.get('status', 'pending')

        if status_filter in ['pending', 'approved', 'rejected']:
            claims = FalseLeadClaim.objects.filter(status=status_filter).order_by('-created_at')
        else:
            claims = FalseLeadClaim.objects.all().order_by('-created_at')

        serializer = FalseLeadClaimSerializer(claims, many=True)

        # Status counts
        counts = {
            "all": FalseLeadClaim.objects.count(),
            "pending": FalseLeadClaim.objects.filter(status="pending").count(),
            "approved": FalseLeadClaim.objects.filter(status="approved").count(),
            "rejected": FalseLeadClaim.objects.filter(status="rejected").count()
        }

        return Response({
            "claims": serializer.data,
            "counts": counts
        }, status=200)
