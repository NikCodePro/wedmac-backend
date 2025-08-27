from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from artists.models.models import ArtistProfile
from adminpanel.models import Service
from artists.serializers.serializers import ArtistServicesSerializer

class ArtistServiceManageView(APIView):
    permission_classes = [IsAuthenticated]

    # def get(self, request):
    #     """Get all services selected by the artist"""
    #     try:
    #         artist_profile = request.user.artist_profile
    #         service_ids = artist_profile.services or []
            
    #         if not service_ids:
    #             return Response([], status=status.HTTP_200_OK)
            
    #         services = Service.objects.filter(id__in=service_ids)
    #         serializer = ArtistServicesSerializer(services, many=True)
    #         return Response(serializer.data, status=status.HTTP_200_OK)
            
    #     except ArtistProfile.DoesNotExist:
    #         return Response(
    #             {"error": "Artist profile not found"}, 
    #             status=status.HTTP_404_NOT_FOUND
    #         )

    # def post(self, request):
    #     """Add services to artist profile"""
    #     try:
    #         artist_profile = request.user.artist_profile
    #         service_ids = request.data.get('service_ids', [])

    #         if not isinstance(service_ids, list):
    #             return Response(
    #                 {"error": "service_ids must be a list"}, 
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )

    #         # Validate service IDs
    #         existing_services = Service.objects.filter(id__in=service_ids)
    #         if len(existing_services) != len(service_ids):
    #             return Response(
    #                 {"error": "Some service IDs are invalid"}, 
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )

    #         # Update artist's services
    #         artist_profile.services = service_ids
    #         artist_profile.save()

    #         # Return updated services
    #         services = Service.objects.filter(id__in=service_ids)
    #         serializer = ArtistServicesSerializer(services, many=True)
    #         return Response(serializer.data, status=status.HTTP_200_OK)

    #     except ArtistProfile.DoesNotExist:
    #         return Response(
    #             {"error": "Artist profile not found"}, 
    #             status=status.HTTP_404_NOT_FOUND
    #         )

    # def delete(self, request):
    #     """Remove services from artist profile"""
    #     try:
    #         artist_profile = request.user.artist_profile
    #         service_ids = request.data.get('service_ids', [])

    #         if not isinstance(service_ids, list):
    #             return Response(
    #                 {"error": "service_ids must be a list"}, 
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )

    #         # Remove specified services
    #         current_services = artist_profile.services or []
    #         updated_services = [s for s in current_services if s not in service_ids]
    #         artist_profile.services = updated_services
    #         artist_profile.save()

    #         # Return remaining services
    #         services = Service.objects.filter(id__in=updated_services)
    #         serializer = ArtistServicesSerializer(services, many=True)
    #         return Response(serializer.data, status=status.HTTP_200_OK)

    #     except ArtistProfile.DoesNotExist:
    #         return Response(
    #             {"error": "Artist profile not found"}, 
    #             status=status.HTTP_404_NOT_FOUND
    #         )