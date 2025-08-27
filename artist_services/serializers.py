from rest_framework import serializers
from .models import Service

class ServiceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating services"""
    class Meta:
        model = Service
        fields = ['name', 'description', 'price']
        read_only_fields = ['artist']

class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for viewing services"""
    artist_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'price', 'created_at', 'updated_at', 'is_active', 'artist_name', 'artist_id']
        read_only_fields = ['id', 'created_at', 'updated_at', 'artist_name', 'artist_id']
    
    def get_artist_name(self, obj):
        return f"{obj.artist.first_name} {obj.artist.last_name}"

class ServiceUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating services"""
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'is_active']