from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from artists.models.models import ArtistProfile
from adminpanel.models import SubscriptionPlan
from artists.serializers.serializers import AdminArtistProfileSerializer
from django.utils import timezone

class AdminSetCurrentPlanView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, artist_id):
        try:
            artist = ArtistProfile.objects.get(id=artist_id)
        except ArtistProfile.DoesNotExist:
            return Response({"error": "Artist not found."}, status=404)

        plan_id = request.data.get("plan_id")
        if not plan_id:
            return Response({"error": "plan_id is required."}, status=400)

        try:
            plan = SubscriptionPlan.objects.get(id=plan_id)
        except SubscriptionPlan.DoesNotExist:
            return Response({"error": "Subscription plan not found."}, status=404)

        # Update the artist's current plan and related fields
        artist.current_plan = plan
        artist.plan_purchase_date = timezone.now()
        artist.plan_verified = True
        artist.available_leads = plan.total_leads
        artist.save()

        serializer = AdminArtistProfileSerializer(artist)
        return Response(serializer.data, status=200)
