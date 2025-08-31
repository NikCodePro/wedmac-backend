from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status as drf_status
from leads.models.models import Lead

class SetMaxClaimsView(APIView):
    """
    Admin-only API to set the maximum number of artists that can claim a lead.
    """
    permission_classes = [IsAdminUser]

    def put(self, request, lead_id):
        try:
            lead = Lead.objects.get(id=lead_id, is_deleted=False)
        except Lead.DoesNotExist:
            return Response({"error": "Lead not found."}, status=drf_status.HTTP_404_NOT_FOUND)

        max_claims = request.data.get('max_claims')

        # Validate max_claims
        if max_claims is None:
            return Response({"error": "max_claims is required."}, status=drf_status.HTTP_400_BAD_REQUEST)

        if not isinstance(max_claims, int) or max_claims < 1:
            return Response({"error": "max_claims must be a positive integer."}, status=drf_status.HTTP_400_BAD_REQUEST)

        # Check if current claimed count exceeds new max_claims
        current_claimed_count = lead.claimed_artists.count()
        if current_claimed_count > max_claims:
            return Response({
                "error": f"Cannot set max_claims to {max_claims}. Lead currently has {current_claimed_count} claimed artists."
            }, status=drf_status.HTTP_400_BAD_REQUEST)

        # Update max_claims
        lead.max_claims = max_claims
        lead.save(update_fields=['max_claims'])

        return Response({
            "message": "Max claims updated successfully.",
            "lead_id": lead.id,
            "max_claims": max_claims,
            "current_claimed_count": current_claimed_count
        }, status=drf_status.HTTP_200_OK)

    def get(self, request, lead_id):
        """
        Get current max_claims for a lead (admin only)
        """
        try:
            lead = Lead.objects.get(id=lead_id, is_deleted=False)
        except Lead.DoesNotExist:
            return Response({"error": "Lead not found."}, status=drf_status.HTTP_404_NOT_FOUND)

        return Response({
            "lead_id": lead.id,
            "max_claims": lead.max_claims,
            "current_claimed_count": lead.claimed_artists.count(),
            "available_slots": max(0, lead.max_claims - lead.claimed_artists.count())
        }, status=drf_status.HTTP_200_OK)
