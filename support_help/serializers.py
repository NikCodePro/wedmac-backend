from rest_framework import serializers
from .models import Ticket

class TicketCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tickets by artists"""
    class Meta:
        model = Ticket
        fields = ['subject', 'category', 'priority', 'description']
        read_only_fields = ['artist', 'status', 'created_at', 'updated_at']

class TicketSerializer(serializers.ModelSerializer):
    """Serializer for viewing tickets"""
    artist_username = serializers.CharField(source='artist.username', read_only=True)
    artist_email = serializers.CharField(source='artist.email', read_only=True)
    
    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ['artist', 'created_at', 'updated_at']

class TicketUpdateSerializer(serializers.ModelSerializer):
    """Serializer for admin to update ticket status"""
    class Meta:
        model = Ticket
        fields = ['status', 'admin_response']