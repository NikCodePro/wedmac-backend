from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db import transaction
from .models import Service
from .serializers import ServiceCreateSerializer, ServiceSerializer, ServiceUpdateSerializer
from rest_framework.permissions import IsAuthenticated
from artists.models.models import ArtistProfile

# Artist Views
class ArtistServiceCreateView(generics.CreateAPIView):
    """Create a new service"""
    serializer_class = ServiceCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        with transaction.atomic():
            # Create the service
            service = serializer.save(artist=self.request.user.artist_profile)
            
            # Update artist's services JSONField
            artist_profile = self.request.user.artist_profile
            current_services = artist_profile.services or []
            current_services.append(service.id)
            artist_profile.services = current_services
            artist_profile.save()
            
            # Store service for create response
            self.created_service = service

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            "message": "Service created successfully",
            "service_id": self.created_service.id,
            "service": ServiceSerializer(self.created_service).data
        }, status=status.HTTP_201_CREATED)
    
class ArtistServiceListView(generics.ListAPIView):
    """List all services created by the authenticated artist"""
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Service.objects.filter(artist=self.request.user.artist_profile)

class ArtistServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a specific service"""
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        return Service.objects.filter(artist=self.request.user.artist_profile)
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ServiceUpdateSerializer
        return ServiceSerializer
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        with transaction.atomic():
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            # Update artist's services if needed
            artist_profile = request.user.artist_profile
            current_services = artist_profile.services or []
            if instance.id not in current_services:
                current_services.append(instance.id)
                artist_profile.services = current_services
                artist_profile.save()

            # Return full service details after update
            full_serializer = ServiceSerializer(instance)
            return Response({
                "message": "Service updated successfully",
                "service": full_serializer.data
            })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        with transaction.atomic():
            # Remove from artist's services list
            artist_profile = request.user.artist_profile
            current_services = artist_profile.services or []
            if instance.id in current_services:
                current_services.remove(instance.id)
                artist_profile.services = current_services
                artist_profile.save()

            # Delete the service
            instance.delete()

            return Response({
                "message": "Service deleted successfully",
                "service_id": kwargs['id']
            }, status=status.HTTP_200_OK)

class ArtistServiceDeleteView(generics.DestroyAPIView):
    """Separate endpoint for deleting a service"""
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Service.objects.filter(artist=self.request.user.artist_profile)

    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                
                # Remove from artist's services list
                artist_profile = request.user.artist_profile
                current_services = artist_profile.services or []
                if instance.id in current_services:
                    current_services.remove(instance.id)
                    artist_profile.services = current_services
                    artist_profile.save()

                # Delete the service
                instance.delete()

                return Response({
                    "message": "Service deleted successfully",
                    "service_id": kwargs['id']
                }, status=status.HTTP_200_OK)

        except Service.DoesNotExist:
            return Response({
                "error": "Service not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)