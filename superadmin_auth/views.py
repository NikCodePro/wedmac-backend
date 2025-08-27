# superadmin_auth/views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError
from django.contrib.auth import authenticate
# from .serializers import SuperAdminLoginSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def superadmin_login(request):
    """Superadmin login endpoint - accepts username/email and password"""
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        print("Username:", username, "Password:", password)

        if not username or not password:
            return Response(
                {'error': 'Please provide both username and password'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if not user:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_superuser:
            return Response(
                {'error': 'User is not authorized as superadmin'},
                status=status.HTTP_403_FORBIDDEN
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
