from datetime import timedelta
from django.utils import timezone

from artists.models.models import ArtistProfile, ArtistSubscription
import razorpay
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from adminpanel.models import SubscriptionPlan
from django.db import transaction
from django.shortcuts import get_object_or_404

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

class PurchaseSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, plan_id):
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id)
        except SubscriptionPlan.DoesNotExist:
            return Response({'error': 'Plan not found'}, status=404)

        artist = ArtistProfile.objects.get(user=request.user)

        if not (artist.status == "approved" or artist.status == "Approved"):
            return Response({'error': 'Artist not approved'}, status=403)

        amount_paise = int(plan.price * 100)
        now  = timezone.now()
        end_date = now + timedelta(days=plan.duration_days) 
        order = client.order.create({
            'amount': amount_paise,
            'currency': 'INR',
            'payment_capture': 1,
            'notes': {
                'plan_id': str(plan_id),
                'artist_id': str(artist.id)
            }
        })

        ArtistSubscription.objects.create(
            artist=artist,
            plan=plan,
            razorpay_order_id=order['id'],
            payment_status='pending',
            end_date=end_date.isoformat(),

        )

        return Response({
            'razorpay_order_id': order['id'],
            'amount': amount_paise,
            'currency': 'INR',
            'key': settings.RAZORPAY_KEY_ID,
            'plan': plan.name,
        })

# class VerifyPaymentView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         try:
#             data = request.data
#             razorpay_order_id = data.get('razorpay_order_id')
#             razorpay_payment_id = data.get('razorpay_payment_id')
#             razorpay_signature = data.get('razorpay_signature')

#             # Verify signature
#             client.utility.verify_payment_signature({
#                 'razorpay_order_id': razorpay_order_id,
#                 'razorpay_payment_id': razorpay_payment_id,
#                 'razorpay_signature': razorpay_signature,
#             })

#             # Activate subscription
#             subscription = ArtistSubscription.objects.get(razorpay_order_id=razorpay_order_id)
#             now = timezone.now()
#             end = now + timedelta(days=subscription.plan.duration_days)

#             subscription.start_date = now
#             subscription.end_date = end
#             subscription.total_leads_allocated = subscription.plan.total_leads
#             subscription.payment_status = 'success'
#             subscription.is_active = True
#             subscription.save()

#             # IMPORTANT: update the related artist profile payment status
#             artist = ArtistProfile.objects.get(id=subscription.artist.id)
#             # set to the value used by ArtistProfile.payment_status field (here 'approved')
#             artist.payment_status = 'approved'

#             # Add plan leads to artist available leads (handle both possible field names)
#             try:
#                 leads_to_add = int(subscription.plan.total_leads or 0)
#             except Exception:
#                 leads_to_add = 0

#             if hasattr(artist, 'available_leads'):
#                 current = int(artist.available_leads or 0)
#                 artist.available_leads = current + leads_to_add
#             elif hasattr(artist, 'available_lead'):
#                 current = int(artist.available_lead or 0)
#                 artist.available_lead = current + leads_to_add
#             else:
#                 # if your model doesn't have a field, create one or log/skip
#                 pass

#             artist.save()

#             return Response({'success': 'Payment verified and subscription activated'}, status=200)

#         except razorpay.errors.SignatureVerificationError:
#             return Response({'error': 'Invalid signature'}, status=400)
#         except ArtistSubscription.DoesNotExist:
#             return Response({'error': 'Subscription not found'}, status=404)
#         except Exception as e:
#             return Response({'error': str(e)}, status=500)

# Update the VerifyPaymentView to use the new credit system
class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        try:
            data = request.data
            razorpay_order_id = data.get('razorpay_order_id')
            razorpay_payment_id = data.get('razorpay_payment_id')
            razorpay_signature = data.get('razorpay_signature')

            if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
                return Response(
                    {'error': 'Missing payment details'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Verify signature
            try:
                client.utility.verify_payment_signature({
                    'razorpay_order_id': razorpay_order_id,
                    'razorpay_payment_id': razorpay_payment_id,
                    'razorpay_signature': razorpay_signature,
                })
            except razorpay.errors.SignatureVerificationError:
                return Response(
                    {'error': 'Invalid payment signature'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get subscription
            subscription = get_object_or_404(
                ArtistSubscription, 
                razorpay_order_id=razorpay_order_id
            )

            # Prevent duplicate activation
            if subscription.payment_status == 'success':
                return Response(
                    {'message': 'Subscription already activated'}, 
                    status=status.HTTP_200_OK
                )

            # Activate subscription and create credits
            now = timezone.now()
            subscription.start_date = now
            subscription.end_date = now + timedelta(days=subscription.plan.duration_days)
            subscription.total_leads_allocated = subscription.plan.total_leads
            subscription.payment_status = 'success'
            subscription.is_active = True
            
            # Use the new method to activate and create credits
            subscription.activate_subscription_and_create_credits()
            subscription.save()
            
            # IMPORTANT: update the related artist profile payment status
            artist = ArtistProfile.objects.get(id=subscription.artist.id)
            # set to the value used by ArtistProfile.payment_status field (here 'approved')
            artist.payment_status = 'approved'
            
            # Add plan leads to artist available leads (handle both possible field names)
            try:
                leads_to_add = int(subscription.plan.total_leads or 0)
            except Exception:
                leads_to_add = 0

            if hasattr(artist, 'available_leads'):
                current = int(artist.available_leads or 0)
                artist.available_leads = current + leads_to_add
            elif hasattr(artist, 'available_lead'):
                current = int(artist.available_lead or 0)
                artist.available_lead = current + leads_to_add
            else:
                # if your model doesn't have a field, create one or log/skip
                pass

            artist.save()

            return Response({
                'success': 'Payment verified and subscription activated',
                'subscription_id': subscription.id,
                'end_date': subscription.end_date.isoformat()
            }, status=status.HTTP_200_OK)

        except ArtistSubscription.DoesNotExist:
            return Response(
                {'error': 'Subscription not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Payment verification failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
