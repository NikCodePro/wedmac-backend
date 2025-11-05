from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from leads.models.models import Lead
from leads.serializers.serializers import LeadSerializer
from django.db.models.functions import Lower
from django.db.models import Q, Count, Prefetch
from django.core.paginator import Paginator
from artists.models.models import ArtistProfile
from django.utils import timezone
from datetime import timedelta
from django.utils.dateparse import parse_datetime

class GetLeadsByStatusView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Get query parameters
            status_param = request.query_params.get('status', 'all').strip().lower()
            page = int(request.query_params.get('page', 1))
            per_page = int(request.query_params.get('per_page', 20))
            
            # Get date range parameters
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            limit = request.query_params.get('limit')

            # Start with base queryset
            leads = Lead.objects.filter(is_deleted=False)

            # Apply date filters
            if start_date and end_date:
                # Convert string dates to datetime
                start_datetime = parse_datetime(start_date) or timezone.make_aware(parse_datetime(f"{start_date}T00:00:00"))
                end_datetime = parse_datetime(end_date) or timezone.make_aware(parse_datetime(f"{end_date}T23:59:59"))
                leads = leads.filter(created_at__range=(start_datetime, end_datetime))
            else:
                # Default to last 40 days if no date range specified and status is 'all'
                if status_param == 'all':
                    forty_days_ago = timezone.now() - timedelta(days=40)
                    leads = leads.filter(created_at__gte=forty_days_ago)

            # Add select_related and prefetch_related to optimize queries
            leads = leads.select_related(
                'service',
                'assigned_to',
                'requested_artist',
                'created_by'
                # Removed 'budget_range' and 'location' since they are not foreign keys
            ).prefetch_related(
                'makeup_types',
                Prefetch('claimed_artists', queryset=ArtistProfile.objects.only('id', 'first_name', 'last_name')),
                Prefetch('booked_artists', queryset=ArtistProfile.objects.only('id', 'first_name', 'last_name'))
            )

            # Apply status filter if needed
            if status_param != 'all':
                leads = leads.annotate(lower_status=Lower('status')).filter(lower_status=status_param)

            # Order by latest first
            leads = leads.order_by('-created_at')

            # Apply limit if specified
            if limit:
                try:
                    limit = int(limit)
                    leads = leads[:limit]
                except ValueError:
                    pass

            # Implement pagination
            paginator = Paginator(leads, per_page)
            page_obj = paginator.get_page(page)

            # Serialize the current page
            serializer = LeadSerializer(page_obj, many=True)
            leads_data = serializer.data

            # Add counts efficiently using annotation
            leads_with_counts = leads.annotate(
                claimed_count=Count('claimed_artists', distinct=True),
                booked_count=Count('booked_artists', distinct=True)
            )

            # Create counts lookup dictionary
            counts_lookup = {
                lead.id: {
                    'claimed_count': lead.claimed_count,
                    'booked_count': lead.booked_count
                }
                for lead in leads_with_counts
            }

            # Add counts to serialized data
            for lead_data in leads_data:
                lead_counts = counts_lookup.get(lead_data['id'], {})
                lead_data['claimed_count'] = lead_counts.get('claimed_count', 0)
                lead_data['booked_count'] = lead_counts.get('booked_count', 0)

            return Response({
                "message": f"Fetched {status_param if status_param != 'all' else 'all'} leads successfully.",
                "count": paginator.count,
                "num_pages": paginator.num_pages,
                "current_page": page,
                "leads": leads_data,
                "filters_applied": {
                    "status": status_param,
                    "start_date": start_date,
                    "end_date": end_date,
                    "limit": limit
                }
            }, status=200)

        except Exception as e:
            return Response({
                "error": str(e),
                "message": "Failed to fetch leads"
            }, status=500)
