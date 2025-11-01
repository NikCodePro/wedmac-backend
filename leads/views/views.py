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
from adminpanel.models import MakeupType



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
        data['is_verified'] = False

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
    Limited to 10 leads per request.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        leads_data = request.data.get('leads', [])
        if not isinstance(leads_data, list):
            return Response({"error": "Expected a list of leads under 'leads' key"}, status=400)

        if len(leads_data) > 10:
            return Response({"error": "Cannot create more than 10 leads at once"}, status=400)

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


class AdminDeleteLeadView(APIView):
    """
    Admin panel view: Admins delete a lead by ID.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, lead_id):
        try:
            lead = Lead.objects.get(id=lead_id)
            lead.delete()
            return Response({"message": "Lead deleted successfully"}, status=200)
        except Lead.DoesNotExist:
            return Response({"error": "Lead not found"}, status=404)


class GetMyAssignedLeadsView(APIView):
    """
    Artist view: Get leads assigned to the logged-in artist.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            artist_profile = request.user.artist_profile
        except:
            return Response({"error": "Artist profile not found."}, status=404)

        leads = Lead.objects.filter(assigned_to=artist_profile, is_deleted=False).order_by('-created_at')
        serializer = LeadSerializer(leads, many=True)
        leads_data = serializer.data

        # Add booked_date for each lead if it's booked
        for i, lead in enumerate(leads):
            if lead.status == 'booked':
                leads_data[i]['booked_date'] = lead.updated_at.date().isoformat()
            else:
                leads_data[i]['booked_date'] = None

        return Response({
            "message": "Assigned leads fetched successfully.",
            "count": leads.count(),
            "leads": leads_data
        }, status=200)


class AdminBulkDeleteLeadsView(APIView):
    """
    Admin panel view: Admins delete multiple leads by IDs.
    Limited to 10 leads per request.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        lead_ids = request.data.get('lead_ids', [])
        if not isinstance(lead_ids, list):
            return Response({"error": "Expected a list of lead IDs under 'lead_ids' key"}, status=400)

        if len(lead_ids) > 10:
            return Response({"error": "Cannot delete more than 10 leads at once"}, status=400)

        deleted_count = 0
        not_found_ids = []

        for lead_id in lead_ids:
            try:
                lead = Lead.objects.get(id=lead_id)
                lead.delete()
                deleted_count += 1
            except Lead.DoesNotExist:
                not_found_ids.append(lead_id)

        response_data = {
            "message": f"Deleted {deleted_count} leads successfully"
        }
        if not_found_ids:
            response_data["not_found_ids"] = not_found_ids

        return Response(response_data, status=200)


class AdminSetLeadVerifiedView(APIView):
    """
    Admin view: Update the is_verified status of a lead.
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, lead_id):
        try:
            lead = Lead.objects.get(id=lead_id)
        except Lead.DoesNotExist:
            return Response({"error": "Lead not found"}, status=404)

        is_verified = request.data.get('is_verified')
        if is_verified is None:
            return Response({"error": "is_verified is required"}, status=400)

        lead.is_verified = is_verified
        lead.save(update_fields=['is_verified'])

        return Response({
            "message": "Lead verification status updated successfully",
            "lead_id": lead.id,
            "is_verified": lead.is_verified
        }, status=200)
