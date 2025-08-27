from django.contrib import admin
from .models import Service

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'artist', 'price', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'price']
    search_fields = ['name', 'description', 'artist__first_name', 'artist__last_name']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('artist')  