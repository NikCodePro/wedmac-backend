from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from appconfig.utils import MasterConfigManager
from leads.models.models import Lead
from leads.serializers.serializers import LeadSerializer
from django.conf import settings
from leads.utils.distribution import assign_lead_automatically
from notifications.services import NotificationService
from users.models import User  # Adjust path if needed



class AdminCreateLeadView(APIView):
    """
    Admin panel view: Admins create leads manually.
    Will auto-assign the lead only if an active distribution strategy exists.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LeadSerializer(data=request.data)
        if serializer.is_valid():
            lead = serializer.save(created_by=request.user)

            # Try assigning automatically (only if strategy is active)
            artist = assign_lead_automatically(lead)

            return Response({
                "message": "Lead created successfully",
                "assigned_to":artist.first_name + " " +artist.last_name +" "+" Mobile:"+ artist.user.username if artist else None,
                "lead": serializer.data
            }, status=201)

        return Response(serializer.errors, status=400)

class PublicLeadSubmissionView(APIView):
    """
    Public site view: A client submits a lead by clicking "Contact" on an artist profile.
    This creates a lead & notifies artist + admin.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # Use a system user or null created_by
        try:
            system_user = User.objects.get(username='system')
        except User.DoesNotExist:
            system_user = None

        data = request.data.copy()
        data['created_by'] = system_user.id if system_user else None

        serializer = LeadSerializer(data=data)
        if serializer.is_valid():
            lead = serializer.save()

            # 🔔 TODO: Trigger notification to artist & admin here
            self.send_lead_notification_to_admin_and_artist(lead)

            return Response({
                "message": "Lead submitted successfully",
                "lead_id": lead.id
            }, status=201)

        return Response(serializer.errors, status=400)


        
    def send_lead_notification_to_admin_and_artist(self,lead):
        """
        Send SMS notifications to:
        - Admins (about new lead submitted for an artist)
        - Requested Artist (that they got a lead)
        """
        config = MasterConfigManager.get_config("NOTIFICATION_NUMBERS")
        admin_numbers = config.get("admin_phone", []) if config else []
        if isinstance(admin_numbers, list):
            admin_numbers = admin_numbers
        elif isinstance(admin_numbers, str):
            admin_numbers = admin_numbers.split(",")
        else:
            admin_numbers = [str(admin_numbers)]        
        artist = lead.requested_artist
        print(f"Requested Artist: {artist}")
        client_name = f"{lead.first_name} {lead.last_name}".strip()
        client_phone = lead.phone
        artist_full_name = f"{artist.first_name} {artist.last_name}" if artist else "N/A"
        
        # Construct message for admins
        message_text = (
            f"New lead submitted for Artist {artist_full_name}.\n"
            f"Client: {client_name}, Phone: {client_phone}\n"
            f"Event: {lead.event_type}, Date: {lead.booking_date}"
        )

        messages = []

        for admin_phone in admin_numbers:
            messages.append({
                "smsFrom": "TFACTR",
                "smsTo": f"+91{admin_phone.strip()[-10:]}",
                "smsText": message_text
            })

        # Send to requested artist if available
        if artist and artist.phone:
            artist_message = (
                f"You've received a new lead from {client_name}.\n"
                f"Event: {lead.event_type}, Booking Date: {lead.booking_date}."
            )
            messages.append({
                "smsFrom": "TFACTR",
                "smsTo": f"+91{artist.phone.strip()[-10:]}",
                "smsText": artist_message
            })
        print(f"Messages to send: {messages}")
        # Send bulk notifications
        response = NotificationService(messages=messages).send_notifications()
        print("Lead Notification Response:", response)
        return response


class AdminCreateMultipleLeadsView(APIView):
    """
    Admin panel view: Admins create multiple leads manually.
    Will auto-assign each lead only if an active distribution strategy exists.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        leads_data = request.data.get('leads', [])
        if not isinstance(leads_data, list):
            return Response({"error": "Expected a list of leads under 'leads' key"}, status=400)

        results = []
        for lead_data in leads_data:
            serializer = LeadSerializer(data=lead_data)
            if serializer.is_valid():
                lead = serializer.save(created_by=request.user)
                # Try assigning automatically (only if strategy is active)
                artist = assign_lead_automatically(lead)
                results.append({
                    "success": True,
                    "lead": serializer.data,
                    "assigned_to": artist.first_name + " " + artist.last_name + " Mobile: " + artist.user.username if artist else None
                })
            else:
                results.append({
                    "success": False,
                    "errors": serializer.errors
                })

        return Response({
            "message": "Bulk lead creation completed",
            "results": results
        }, status=200)
