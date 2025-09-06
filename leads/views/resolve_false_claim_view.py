from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from artists.models.models import ArtistSubscription
from leads.models.false_lead_claim import FalseLeadClaim
from users.permissions import IsAdminRole
from django.utils import timezone
from notifications.services import NotificationService
from django.db import transaction
from superadmin_auth.permissions import IsSuperAdmin

class ResolveFalseClaimView(APIView):
    permission_classes = [IsSuperAdmin]

    def patch(self, request, pk):
        with transaction.atomic():
            try:
                claim = FalseLeadClaim.objects.select_for_update().get(id=pk)
            except FalseLeadClaim.DoesNotExist:
                return Response({"error": "False claim not found."}, status=404)

            new_status = request.data.get("status")
            admin_note = request.data.get("admin_note", "")

            if new_status not in ["approved", "rejected"]:
                return Response({"error": "Invalid status. Choose 'approved' or 'rejected'."}, status=400)

            # Update claim
            claim.status = new_status
            claim.admin_note = admin_note
            claim.resolved_by = request.user
            claim.resolved_at = timezone.now()
            claim.save()

            # Get artist and phone number
            artist = claim.artist
            artist_phone = artist.phone if artist.phone else ""

            # Handle claim approval → restore lead
            if new_status == "approved":
                # Restore one lead
                artist.available_leads += 1
                artist.save()
                
                # Add notification message about restored lead
                message = (
                    f"Hi {artist.first_name}, your false lead claim (ID #{claim.id}) "
                    "has been approved. One lead has been restored to your account."
                )
            else:
                message = (
                    f"Hi {artist.first_name}, your false lead claim (ID #{claim.id}) "
                    f"has been rejected. Admin note: {admin_note or 'No reason provided.'}"
                )

            # Initialize messages list for notifications
            notification_messages = [{
                "smsFrom": "TFACTR",
                "smsTo": f"+91{artist_phone}",
                "smsText": message
            }]

            try:
                # Send notification
                response = NotificationService(messages=notification_messages).send_notifications()
                print("False Claim Notification Response:", response)
            except Exception as e:
                print(f"Notification failed: {str(e)}")
                # Continue execution even if notification fails

            return Response({
                "message": f"Claim #{claim.id} marked as {new_status}",
                "status": new_status,
                "notification_sent": True
            }, status=200)
