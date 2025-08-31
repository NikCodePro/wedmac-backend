from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status as drf_status
from leads.models.models import Lead

class BulkSetMaxClaimsView(APIView):
    """
    Admin-only API to set the maximum number of artists that can claim ALL leads at once.
    """
    permission_classes = [IsAdminUser]

    def put(self, request):
        max_claims = request.data.get('max_claims')

        # Validate max_claims
        if max_claims is None:
            return Response({"error": "max_claims is required."}, status=drf_status.HTTP_400_BAD_REQUEST)

        if not isinstance(max_claims, int) or max_claims < 1:
            return Response({"error": "max_claims must be a positive integer."}, status=drf_status.HTTP_400_BAD_REQUEST)

        # Get all non-deleted leads
        leads = Lead.objects.filter(is_deleted=False)

        if not leads.exists():
            return Response({"error": "No leads found to update."}, status=drf_status.HTTP_404_NOT_FOUND)

        # Check if any lead has more claimed artists than the new max_claims
        problematic_leads = []
        for lead in leads:
            current_claimed_count = lead.claimed_artists.count()
            if current_claimed_count > max_claims:
                problematic_leads.append({
                    "lead_id": lead.id,
                    "current_claimed_count": current_claimed_count
                })

        if problematic_leads:
            return Response({
                "error": f"Cannot set max_claims to {max_claims}. The following leads have more claimed artists:",
                "problematic_leads": problematic_leads
            }, status=drf_status.HTTP_400_BAD_REQUEST)

        # Update all leads with the new max_claims
        updated_count = leads.update(max_claims=max_claims)

        return Response({
            "message": f"Max claims updated successfully for {updated_count} leads.",
            "max_claims": max_claims,
            "total_leads_updated": updated_count
        }, status=drf_status.HTTP_200_OK)

    def get(self, request):
        """
        Get current max_claims statistics for all leads (admin only)
        """
        leads = Lead.objects.filter(is_deleted=False)

        if not leads.exists():
            return Response({"error": "No leads found."}, status=drf_status.HTTP_404_NOT_FOUND)

        # Calculate statistics
        total_leads = leads.count()
        leads_with_max_claims = leads.filter(max_claims__isnull=False).count()
        leads_without_max_claims = total_leads - leads_with_max_claims

        # Get distribution of max_claims values
        max_claims_distribution = {}
        for lead in leads:
            if lead.max_claims is not None:
                key = str(lead.max_claims)
                max_claims_distribution[key] = max_claims_distribution.get(key, 0) + 1

        # Get overall statistics
        total_claimed_artists = sum(lead.claimed_artists.count() for lead in leads)
        total_booked_artists = sum(lead.booked_artists.count() for lead in leads)

        return Response({
            "total_leads": total_leads,
            "leads_with_max_claims": leads_with_max_claims,
            "leads_without_max_claims": leads_without_max_claims,
            "max_claims_distribution": max_claims_distribution,
            "total_claimed_artists": total_claimed_artists,
            "total_booked_artists": total_booked_artists,
            "average_claims_per_lead": round(total_claimed_artists / total_leads, 2) if total_leads > 0 else 0
        }, status=drf_status.HTTP_200_OK)
