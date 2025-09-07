# artists/serializers/website/artist_public_detail_serializer.py

from rest_framework import serializers
from artists.models.models import ArtistProfile, SocialLink
from documents.models import Document
from artist_services.models import Service
from .payment_method_serializer import PaymentMethodSerializer


class DocumentURLSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['file_url', 'file_type', 'tag']
class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLink
        fields = ['platform', 'url']



class ArtistPublicDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    makeup_types = serializers.SerializerMethodField()
    products_used = serializers.SerializerMethodField()
    profile_photo_url = serializers.SerializerMethodField()
    portfolio_photos = serializers.SerializerMethodField()
    services = serializers.SerializerMethodField()
    certifications = DocumentURLSerializer(many=True)
    social_links = SocialLinkSerializer(many=True, read_only=True)
    payment_methods = PaymentMethodSerializer(many=True, read_only=True)
    
    class Meta:
        model = ArtistProfile
        fields = [
            'id',
            'full_name',
            'location',
            'bio',
            'makeup_types',
            'price_range',
            'products_used',
            'experience_years',
            'services',
            'travel_charges',
            'trial_available',
            'social_links',
            'average_rating',
            'total_ratings',
            'profile_photo_url',
            'portfolio_photos',
            'certifications',
            'travel_policy',
            'trial_available',
            'travel_charges',
            'payment_methods',
            'travel_policy',
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_location(self, obj):
        if obj.location:
            return {
                "city": obj.location.city,
                "state": obj.location.state
            }
        return None

    def get_makeup_types(self, obj):
        return [mt.name for mt in obj.type_of_makeup.all()]

    def get_products_used(self, obj):
        return [p.name for p in obj.products_used.all()]

    def get_profile_photo_url(self, obj):
        return obj.profile_picture.file_url if obj.profile_picture else None

    def get_portfolio_photos(self, obj):
        return [doc.file_url for doc in obj.supporting_images.all()]

    def get_services(self, obj):
        """Return service data from artist_services table"""
        services = obj.services_offered.filter(is_active=True)
        return [{
            'id': service.id,
            'name': service.name,
            'description': service.description,
            'price': str(service.price),
            'created_at': service.created_at,
            'updated_at': service.updated_at
        } for service in services]
