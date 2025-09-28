# users/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from artists.models.models import ArtistProfile , Location
import random
from django.utils import timezone
from notifications.services import TwoFactorService
from notifications.services import NotificationService
from users.models import OTPVerification, User


# User login with OTP
class RequestLoginOTPView(APIView):
    permission_classes = [AllowAny]
    """
    This view handles the request for an OTP to be sent to the user's phone for login purposes.
    It checks if the user exists based on the provided phone number, generates an OTP,
    and saves it in the OTPVerification model."""

    def post(self, request):
        phone = request.data.get("phone")
        if not phone:
            return Response({"error": "Phone is required."}, status=400)

        try:
            user = User.objects.get(phone=phone)
            print(f"User found: {user.username} with phone {user.phone}")
            print(f"User OTP verified status: {user.otp_verified}")
            if not user.is_active:
                return Response({"error": "User is inactive."}, status=403)
            if not user.otp_verified:
                return Response({"error": "User's OTP is not verified."}, status=403)
            # Generate OTP
            otp = str(random.randint(100000, 999999))
            # Save OTP in OTPVerification model
            OTPVerification.objects.create(phone=phone, otp=otp)
            response = TwoFactorService(phone=phone, otp=otp).send_otp()
            if response.get('Status') != 'Success':
                return Response({'error': response.get('error', 'Failed to send OTP.')}, status=500)
            # For now, return OTP in response (in real app, send via SMS)
            return Response({"message": "Login OTP sent successfully.", "otp": otp}, status=200)

        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)



class OTPLoginView(APIView):
    permission_classes = [AllowAny]
    """ 
        This view handles the login process using an OTP.
        It verifies the OTP against the OTPVerification model and
        if valid, generates JWT tokens for the user.
        It also checks if the OTP is expired (5 minutes validity).
        If the OTP is valid and not expired, it returns a success response with JWT tokens.
        If the OTP is invalid or expired, it returns an error response.
    """

    def post(self, request):
        phone = request.data.get('phone')
        otp = request.data.get('otp')

        if not phone or not otp:
            return Response({'error': 'Phone and OTP are required.'}, status=400)

        try:
            otp_obj = OTPVerification.objects.filter(phone=phone, otp=otp).latest('created_at')
            # Check if OTP is expired
            if otp_obj.is_expired():
                return Response({'error': 'OTP has expired.'}, status=400)
            # Verify OTP using TwoFactorService
            response = TwoFactorService(phone=phone, otp=otp).verify_otp()
            print(f"OTP verification response: {response}")
            if response.get('Status') == 'Success': # 'Success' means OTP verification successful
                user = User.objects.get(phone=phone)
                # Mark user as verified after successful OTP verification
                user.otp_verified = True
                user.save(update_fields=['otp_verified'])
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': 'Login successful.',
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user_id': user.id,
                    'role': user.role,
                })
            return Response({'error': 'Invalid OTP.'}, status=400)
        except OTPVerification.DoesNotExist:
            return Response({'error': 'Invalid OTP.'}, status=400)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)