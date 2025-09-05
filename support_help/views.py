from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Ticket
from .serializers import TicketCreateSerializer, TicketSerializer, TicketUpdateSerializer
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
from rest_framework.permissions import IsAuthenticated
from superadmin_auth.permissions import IsSuperAdmin

class ArtistTicketCreateView(generics.CreateAPIView):
    """Artists can create tickets"""
    serializer_class = TicketCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(artist=self.request.user)

class ArtistTicketListView(generics.ListAPIView):
    """Artists can view their own tickets"""
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Ticket.objects.filter(artist=self.request.user)

class ArtistTicketDetailView(generics.RetrieveAPIView):
    """Artists can view their own ticket details"""
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Ticket.objects.filter(artist=self.request.user)

class AdminTicketListView(generics.ListAPIView):
    """Admins can view all tickets"""
    serializer_class = TicketSerializer
    permission_classes = [IsSuperAdmin]
    
    def get_queryset(self):
        queryset = Ticket.objects.select_related('artist')
        
        # Optional filtering
        status_filter = self.request.query_params.get('status', None)
        priority_filter = self.request.query_params.get('priority', None)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
            
        return queryset

class AdminTicketUpdateView(generics.UpdateAPIView):
    """Admins can update ticket status and add response"""
    serializer_class = TicketUpdateSerializer
    permission_classes = [IsSuperAdmin]
    queryset = Ticket.objects.all()
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Return full ticket details after update
        full_serializer = TicketSerializer(instance)
        return Response(full_serializer.data)
    
    
class AdminTicketDeleteView(generics.DestroyAPIView):
    """Admins can delete tickets"""
    permission_classes = [IsSuperAdmin]
    queryset = Ticket.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Ticket deleted successfully."}, status=status.HTTP_200_OK)

# Alternative function-based views for more control
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def artist_tickets_summary(request):
    """Get summary of artist's tickets"""
    tickets = Ticket.objects.filter(artist=request.user)
    
    summary = {
        'total_tickets': tickets.count(),
        'open_tickets': tickets.filter(status='open').count(),
        'in_progress_tickets': tickets.filter(status='in_progress').count(),
        'resolved_tickets': tickets.filter(status='resolved').count(),
    }
    
    return Response(summary)

class AdminDashboardStatsView(generics.GenericAPIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        total_tickets = Ticket.objects.count()
        open_tickets = Ticket.objects.filter(status='open').count()
        in_progress_tickets = Ticket.objects.filter(status='in_progress').count()
        resolved_tickets = Ticket.objects.filter(status='resolved').count()
        closed_tickets = Ticket.objects.filter(status='closed').count()

        # Calculate average response time (time between created_at and first admin_response)
        # For simplicity, assuming admin_response is set when response is made
        tickets_with_response = Ticket.objects.exclude(admin_response__isnull=True).exclude(admin_response__exact='')
        avg_response_time = tickets_with_response.annotate(
            response_time=ExpressionWrapper(
                F('updated_at') - F('created_at'),
                output_field=DurationField()
            )
        ).aggregate(avg_response=Avg('response_time'))['avg_response']

        # Calculate average resolution time (time between created_at and resolved_at)
        tickets_with_resolution = Ticket.objects.filter(resolved_at__isnull=False)
        avg_resolution_time = tickets_with_resolution.annotate(
            resolution_time=ExpressionWrapper(
                F('resolved_at') - F('created_at'),
                output_field=DurationField()
            )
        ).aggregate(avg_resolution=Avg('resolution_time'))['avg_resolution']

        # Convert durations to hours float
        def duration_to_hours(duration):
            if duration is None:
                return None
            return duration.total_seconds() / 3600

        data = {
            "overview": {
                "total_tickets": total_tickets,
                "open_tickets": open_tickets,
                "in_progress_tickets": in_progress_tickets,
                "resolved_tickets": resolved_tickets,
                "closed_tickets": closed_tickets,
            },
            "performance_metrics": {
                "average_response_time_hours": duration_to_hours(avg_response_time),
                "average_resolution_time_hours": duration_to_hours(avg_resolution_time),
            }
        }
        return Response(data)