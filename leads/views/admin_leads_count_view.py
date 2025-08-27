# views/admin_lead_count_view.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models.functions import Lower
from django.db.models import Count
from leads.models.models import Lead

class AdminLeadStatusCountView(APIView):
    """
    Returns lead counts grouped by status for admin dashboard.
    Only includes non-deleted leads.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        status_counts = (
            Lead.objects
            .filter(is_deleted=False)
            .annotate(status_lower=Lower('status'))
            .values('status_lower')
            .annotate(count=Count('id'))
            .order_by()
        )

        result = {
            "new": 0,
            "contacted": 0,
            "qualified": 0,
            "unqualified": 0,
            "converted": 0
        }

        for item in status_counts:
            status = item['status_lower']
            count = item['count']
            if status in result:
                result[status] = count

        return Response(result)
