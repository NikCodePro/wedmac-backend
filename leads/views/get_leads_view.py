from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from leads.models.models import Lead
from leads.serializers.serializers import LeadSerializer
from django.db.models.functions import Lower
from django.db.models import Q

class GetLeadsByStatusView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        status_param = request.query_params.get('status', 'all').strip().lower()

        leads = Lead.objects.filter(is_deleted=False)

        if status_param != 'all':
            leads = leads.annotate(lower_status=Lower('status')).filter(lower_status=status_param)

        serializer = LeadSerializer(leads.order_by('-created_at'), many=True)
        return Response({
            "message": f"Fetched {status_param if status_param != 'all' else 'all'} leads successfully.",
            "count": leads.count(),
            "leads": serializer.data
        }, status=200)
