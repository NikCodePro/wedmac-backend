from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from .razorpay_client import client, verify_razorpay_signature
from artists.models.models import ArtistProfile
from adminpanel.models import SubscriptionPlan

class CreateOrderView(APIView):
    def post(self, request, plan_id):
        artist = ArtistProfile.objects.get(user=request.user)
        plan = SubscriptionPlan.objects.get(id=plan_id)

        amount = int(plan.price * 100)  # in paise

        order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1,
            "notes": {
                "artist_id": artist.id,
                "plan_id": plan.id
            }
        })

        return Response({
            "razorpay_order_id": order['id'],
            "amount": amount,
            "currency": "INR",
            "key": settings.RAZORPAY_KEY_ID
        })


class VerifyPaymentView(APIView):
    def post(self, request):
        data = request.data
        order_id = data.get("razorpay_order_id")
        payment_id = data.get("razorpay_payment_id")
        signature = data.get("razorpay_signature")

        if not verify_razorpay_signature(order_id, payment_id, signature):
            return Response({"error": "Signature verification failed"}, status=400)

        # You can store subscription logic here (retrieve artist_id & plan_id from notes via webhook or pass manually)
        return Response({"success": "Payment verified"})
