# content_management/admin.py

from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Customizes the Review model's representation in the Django admin.
    """
    # Display these fields in the list view of the admin panel.
    list_display = ('client_name', 'used_service', 'rating', 'created_at')

    # Add a search bar to search through these fields.
    search_fields = ('client_name', 'used_service', 'description')

    # Add filters to the right sidebar.
    list_filter = ('rating', 'used_service', 'created_at')

    # Add a date hierarchy for easy navigation by date.
    date_hierarchy = 'created_at'
