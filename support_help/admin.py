from django.contrib import admin
from .models import Ticket

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['subject', 'artist', 'category', 'priority', 'status', 'created_at']
    list_filter = ['status', 'priority', 'category', 'created_at']
    search_fields = ['subject', 'description', 'artist__username']
    readonly_fields = ['created_at', 'updated_at', 'resolved_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('artist')