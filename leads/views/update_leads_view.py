from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status as drf_status
from django.utils import timezone
from leads.models.models import Lead
from leads.serializers.serializers import LeadSerializer

class UpdateLeadView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, lead_id):
        try:
            lead = Lead.objects.get(id=lead_id)
        except Lead.DoesNotExist:
            return Response({"error": "Lead not found."}, status=drf_status.HTTP_404_NOT_FOUND)

        data = request.data.copy()

        # Handle soft delete
        if str(data.get("is_deleted")).lower() == "true":
            lead.is_deleted = True
            lead.deleted_at = timezone.now()
            lead.save()
            return Response({"message": "Lead soft-deleted successfully."}, status=drf_status.HTTP_200_OK)

        # Normalize status if provided
        if "status" in data:
            status_value = data["status"].lower()
            valid_statuses = [s[0].lower() for s in Lead.STATUS_CHOICES]
            if status_value not in valid_statuses:
                return Response({"error": "Invalid status provided."}, status=drf_status.HTTP_400_BAD_REQUEST)
        if "assigned_to" in data:
            assigned_to = data["assigned_to"]
            if not isinstance(assigned_to, int):
                return Response({"error": "Assigned to must be a valid user ID."}, status=drf_status.HTTP_400_BAD_REQUEST)
            # Additional validation can be added here to check if the user exists

        # Partial update using serializer
        serializer = LeadSerializer(lead, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Lead updated successfully.", "lead": serializer.data}, status=drf_status.HTTP_200_OK)
        
        return Response(serializer.errors, status=drf_status.HTTP_400_BAD_REQUEST)
