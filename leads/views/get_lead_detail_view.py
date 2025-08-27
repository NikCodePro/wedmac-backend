# views/get_lead_detail.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from leads.models.models import Lead
from leads.serializers.serializers import LeadDetailSerializer

class LeadDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, lead_id):
        try:
            lead = Lead.objects.get(pk=lead_id, is_deleted=False)
        except Lead.DoesNotExist:
            return Response({"error": "Lead not found."}, status=404)

        serializer = LeadDetailSerializer(lead)
        return Response(serializer.data, status=200)
