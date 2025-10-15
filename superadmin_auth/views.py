# superadmin_auth/views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model, authenticate
from users.models import OTPVerification
from notifications.services import TwoFactorService
import random
from django.utils import timezone
import os
# from .serializers import SuperAdminLoginSerializer

User = get_user_model()

# Master OTP for superadmin login (should be set as environment variable in production)
MASTER_OTP = os.getenv('SUPERADMIN_MASTER_OTP')  # Default for testing

@api_view(['POST'])
@permission_classes([AllowAny])
def superadmin_login(request):
    """Superadmin login endpoint - sends OTP via call"""
    try:
        phone = request.data.get('phone')
        print("Phone:", phone)

        if not phone:
            return Response(
                {'error': 'Please provide phone number'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(phone=phone, is_superuser=True)
        except User.DoesNotExist:
            return Response(
                {'error': 'Superadmin not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        otp = str(random.randint(100000, 999999))
        OTPVerification.objects.create(phone=phone, otp=otp)

        # Send OTP via call
        service = TwoFactorService(phone=phone, otp=otp, mode="call")
        response = service.send_otp()
        print("OTP send response:", response)

        return Response({
            'message': 'OTP sent via call'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def superadmin_verify_otp(request):
    """Verify OTP and login superadmin"""
    try:
        phone = request.data.get('phone')
        otp = request.data.get('otp')

        if not phone or not otp:
            return Response(
                {'error': 'Please provide phone and OTP'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if master OTP is used
        if otp == MASTER_OTP:
            # Master OTP used, skip regular OTP verification
            pass
        else:
            # Regular OTP verification
            otp_obj = OTPVerification.objects.filter(phone=phone, otp=otp).first()

            if not otp_obj or otp_obj.is_expired():
                return Response(
                    {'error': 'Invalid or expired OTP'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # OTP valid, delete it
            otp_obj.delete()

        try:
            user = User.objects.get(phone=phone, is_superuser=True)
        except User.DoesNotExist:
            return Response(
                {'error': 'Superadmin not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'username': user.username,
            'is_superuser': user.is_superuser
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def superadmin_profile(request):
    """Get superadmin profile - requires JWT authentication"""
    if not request.user.is_superuser:
        return Response(
            {'error': 'Not authorized'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    return Response({
        'id': request.user.id,
        'username': request.user.username,
        'email': request.user.email,
        'is_superuser': request.user.is_superuser
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def superadmin_logout(request):
    """Superadmin logout - blacklist refresh token"""
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(
            {'message': 'Successfully logged out'},
            status=status.HTTP_200_OK
        )
    except Exception:
        return Response(
            {'error': 'Invalid token'},
            status=status.HTTP_400_BAD_REQUEST
        )
