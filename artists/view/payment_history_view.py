from django.utils import timezone
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from artists.models.models import ArtistProfile, ArtistSubscription
from adminpanel.models import SubscriptionPlan

from superadmin_auth.permissions import IsSuperAdmin

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
                    "id": str(sub.plan.id) if sub.plan else None,
                    "name": sub.plan.name if sub.plan else None,
                    "price": str(sub.plan.price) if sub.plan and hasattr(sub.plan, 'price') else None,
                    "duration_days": sub.plan.duration_days if sub.plan and hasattr(sub.plan, 'duration_days') else None,
                    "total_leads": sub.plan.total_leads if sub.plan and hasattr(sub.plan, 'total_leads') else None,
                },
                "payment": {
                    "status": sub.payment_status,
                    "is_active": sub.is_active,
                    "razorpay_order_id": getattr(sub, 'razorpay_order_id', None),
                    # Optionally include more fields if present:
                    # "razorpay_payment_id": getattr(sub, 'razorpay_payment_id', None),
                },
                "dates": {
                    "start_date": sub.start_date,
                    "end_date": sub.end_date,
                    "created_at": sub.created_at,
                },
                "usage": {
                    "total_leads_allocated": getattr(sub, 'total_leads_allocated', None),
                    "leads_used": getattr(sub, 'leads_used', None),
                    "remaining_leads": max(0, (getattr(sub, 'total_leads_allocated', 0) or 0) - (getattr(sub, 'leads_used', 0) or 0)),
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


# Admin API to get all artists' payment history with filters
class AdminArtistPaymentHistoryView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        # Filters
        artist_id = request.query_params.get("artist_id")
        status_param = request.query_params.get("status")
        is_active_param = request.query_params.get("is_active")
        start_date = request.query_params.get("start_date")  # YYYY-MM-DD
        end_date = request.query_params.get("end_date")      # YYYY-MM-DD
        limit = int(request.query_params.get("limit", 20))
        offset = int(request.query_params.get("offset", 0))

        qs = ArtistSubscription.objects.select_related("artist", "plan").all().order_by("-created_at")

        if artist_id:
            qs = qs.filter(artist__id=artist_id)
        if status_param in ("pending", "success", "failed"):
            qs = qs.filter(payment_status=status_param)
        if is_active_param is not None:
            if is_active_param.lower() == "true":
                qs = qs.filter(is_active=True)
            elif is_active_param.lower() == "false":
                qs = qs.filter(is_active=False)
        if start_date:
            try:
                qs = qs.filter(created_at__date__gte=start_date)
            except Exception:
                pass
        if end_date:
            try:
                qs = qs.filter(created_at__date__lte=end_date)
            except Exception:
                pass

        total = qs.count()
        items = qs[offset: offset + limit]

        # Serialize results (simple dict)
        results = []
        for sub in items:
            results.append({
                "id": sub.id,
                "artist_id": sub.artist.id if sub.artist else None,
                "artist_name": f"{sub.artist.first_name} {sub.artist.last_name}" if sub.artist else None,
                "plan": sub.plan.name if sub.plan else None,
                "amount": sub.amount if hasattr(sub, 'amount') else None,
                "payment_status": sub.payment_status,
                "is_active": sub.is_active,
                "start_date": sub.start_date,
                "end_date": sub.end_date,
                "created_at": sub.created_at,
                "razorpay_order_id": getattr(sub, 'razorpay_order_id', None),
            })

        return Response({
            "total": total,
            "results": results
        }, status=status.HTTP_200_OK)
        # results.append({
        #     "id": sub.id,
        #     "plan": {
        #         "id": str(sub.plan.id),
        #         "name": sub.plan.name,
        #         "price": str(sub.plan.price),
        #         "duration_days": sub.plan.duration_days,
        #         "total_leads": sub.plan.total_leads,
        #     },
        #     "payment": {
        #         "status": sub.payment_status,        # pending | success | failed
        #         "is_active": sub.is_active,
        #         "razorpay_order_id": sub.razorpay_order_id,
        #         # include if present in your model:
        #         # "razorpay_payment_id": sub.razorpay_payment_id,
        #     },
        #     "dates": {
        #         "start_date": sub.start_date,
        #         "end_date": sub.end_date,
        #         "created_at": sub.created_at,
        #     },
        #     "usage": {
        #         "total_leads_allocated": sub.total_leads_allocated,
        #         "leads_used": sub.leads_used,
        #         "remaining_leads": max(0, (sub.total_leads_allocated or 0) - (sub.leads_used or 0)),
        #     }
        # })

        # response = {
        #     "artist": {
        #         "id": artist.id,
        #         "name": f"{artist.first_name} {artist.last_name}",
        #         "user_id": artist.user_id,
        #         "phone": artist.phone,
        #         "email": artist.email,
        #         "status": artist.status,
        #     },
        #     "count": total,
        #     "limit": limit,
        #     "offset": offset,
        #     "results": results
        # }
        # return Response(response, status=status.HTTP_200_OK)

