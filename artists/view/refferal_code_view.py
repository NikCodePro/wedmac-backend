from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from artists.models.models import ArtistProfile
from artists.serializers.serializers import ArtistProfileSerializer, ReferralCodeSerializer
from rest_framework.permissions import IsAuthenticated

# API to generate referral code
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_referral_code(request):
    """
    Generate referral code for authenticated artist
    """
    try:
        artist_profile = request.user.artist_profile
        
        # Check if referral code already exists
        if artist_profile.my_referral_code:  # Changed to match your model field
            return Response({
                'message': 'Referral code already exists',
                'referral_code': artist_profile.my_referral_code
            }, status=status.HTTP_200_OK)
        
        # Generate new referral code
        # Generate unique referral code based on first name and random string
        base_name = artist_profile.first_name.replace(' ', '').upper()[:6] if artist_profile.first_name else 'ARTIST'
        random_part = get_random_string(5, '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        referral_code = f"{base_name}{random_part}"
        
        # Save the referral code
        artist_profile.my_referral_code = referral_code  # Changed to match your model field
        artist_profile.save()
        
        return Response({
            'message': 'Referral code generated successfully',
            'referral_code': referral_code
        }, status=status.HTTP_201_CREATED)
        
    except ArtistProfile.DoesNotExist:
        return Response({
            'error': 'Artist profile not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# API to get referral code
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_referral_code(request):
    """
    Get referral code for authenticated artist
    """
    try:
        artist_profile = request.user.artist_profile
        
        if not artist_profile.my_referral_code:  # Changed to match your model field
            return Response({
                'message': 'No referral code generated yet',
                'referral_code': None
            }, status=status.HTTP_200_OK)
        
        return Response({
            'referral_code': artist_profile.my_referral_code  # Changed to match your model field
        }, status=status.HTTP_200_OK)
        
    except ArtistProfile.DoesNotExist:
        return Response({
            'error': 'Artist profile not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ArtistProfileDetailView(generics.RetrieveAPIView):
    """Get artist profile details including referral code"""
    serializer_class = ArtistProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user.artist_profile