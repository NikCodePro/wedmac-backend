from django.utils import timezone
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from artists.models.models import ArtistProfile, ArtistSubscription
from adminpanel.models import SubscriptionPlan
# from rest_framework.permissions import IsArtistOrSuperAdmin # path adjusted if needed

class ArtistPaymentHistoryView(APIView):
    # auth_checker = IsArtistOrSuperAdmin()
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # 1) Resolve artist
        artist_id = request.query_params.get("artist_id")
        if artist_id:
            try:
                artist = ArtistProfile.objects.select_related("user").get(id=artist_id)
            except ArtistProfile.DoesNotExist:
                return Response({"error": "Artist not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # No artist_id provided: must be the artist themself
            try:
                artist = ArtistProfile.objects.select_related("user").get(user=request.user)
            except ArtistProfile.DoesNotExist:
                return Response({"error": "Artist profile not found for current user"}, status=status.HTTP_404_NOT_FOUND)

        # 2) Filters
        qs = (
            ArtistSubscription.objects
            .filter(artist=artist)
            .select_related("plan")
            .order_by("-created_at")
        )

        status_param = request.query_params.get("status")
        if status_param in ("pending", "success", "failed"):
            qs = qs.filter(payment_status=status_param)

        is_active_param = request.query_params.get("is_active")
        if is_active_param is not None:
            if is_active_param.lower() in ("true", "1", "yes"):
                qs = qs.filter(is_active=True)
            elif is_active_param.lower() in ("false", "0", "no"):
                qs = qs.filter(is_active=False)

        start_date = request.query_params.get("start_date")  # YYYY-MM-DD
        end_date = request.query_params.get("end_date")      # YYYY-MM-DD

        if start_date:
            qs = qs.filter(created_at__date__gte=start_date)
        if end_date:
            qs = qs.filter(created_at__date__lte=end_date)

        # 3) Pagination: limit/offset
        try:
            limit = int(request.query_params.get("limit", 20))
            offset = int(request.query_params.get("offset", 0))
        except ValueError:
            return Response({"error": "limit and offset must be integers"}, status=status.HTTP_400_BAD_REQUEST)

        total = qs.count()
        items = qs[offset: offset + limit]

        # 4) Serialize without creating a dedicated serializer (simple, explicit dict)
        results = []
        for sub in items:
            results.append({
                "id": sub.id,
                "plan": {
                    "id": str(sub.plan.id),
                    "name": sub.plan.name,
                    "price": str(sub.plan.price),
                    "duration_days": sub.plan.duration_days,
                    "total_leads": sub.plan.total_leads,
                },
                "payment": {
                    "status": sub.payment_status,        # pending | success | failed
                    "is_active": sub.is_active,
                    "razorpay_order_id": sub.razorpay_order_id,
                    # include if present in your model:
                    # "razorpay_payment_id": sub.razorpay_payment_id,
                },
                "dates": {
                    "start_date": sub.start_date,
                    "end_date": sub.end_date,
                    "created_at": sub.created_at,
                },
                "usage": {
                    "total_leads_allocated": sub.total_leads_allocated,
                    "leads_used": sub.leads_used,
                    "remaining_leads": max(0, (sub.total_leads_allocated or 0) - (sub.leads_used or 0)),
                }
            })

        response = {
            "artist": {
                "id": artist.id,
                "name": f"{artist.first_name} {artist.last_name}",
                "user_id": artist.user_id,
                "phone": artist.phone,
                "email": artist.email,
                "status": artist.status,
            },
            "count": total,
            "limit": limit,
            "offset": offset,
            "results": results
        }
        return Response(response, status=status.HTTP_200_OK)

