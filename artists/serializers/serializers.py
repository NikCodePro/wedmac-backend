from rest_framework import serializers
from artists.models.models import ArtistProfile, ArtistSubscription, SocialLink
from documents.models import Document
from adminpanel.models import MakeupType, Product, PaymentMethod, SubscriptionPlan
from artists.models.models import Location
from adminpanel.models import Service
from artist_services.models import Service as ArtistService
import base64


# Document Serializer
class DocumentSerializer(serializers.ModelSerializer):
    file_base64 = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'file_name', 'file_type', 'tag', 'created_at',
            'file_url', 'public_id', 'is_active', 'file_base64'
        ]

    def get_file_base64(self, obj):
        # Handle both single Document and ManyRelatedManager
        if hasattr(obj, 'file_data'):
            if obj.file_data:
                return base64.b64encode(obj.file_data).decode('utf-8')
        return None


# Related Serializers
class SocialLinkSerializer(serializers.ModelSerializer):
    url = serializers.URLField(allow_blank=True, required=False)

    class Meta:
        model = SocialLink
        fields = ['platform', 'url']


class MakeupTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MakeupType
        fields = ['id', 'name']  # Adjust based on model fields

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'city', 'state', 'pincode', 'lat', 'lng']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name','description']  # Adjust based on model fields
        
class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['id', 'name', 'description']  # Adjust based on model fields

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'price', 'total_leads', 'duration_days']  # Adjust based on actual fields


# Main ArtistProfile Serializer
class ArtistProfileSerializer(serializers.ModelSerializer):
    # READ FIELDS
    type_of_makeup = MakeupTypeSerializer(many=True, read_only=True)
    products_used_data = ProductSerializer(source='products_used', many=True, read_only=True)
    payment_methods_data = PaymentMethodSerializer(source='payment_methods', many=True, read_only=True)
    social_links_data = SocialLinkSerializer(source='social_links', many=True, read_only=True)
    services_offered = serializers.SerializerMethodField()

    location = LocationSerializer(read_only=True)
    current_plan = SubscriptionPlanSerializer(read_only=True)

    # WRITE FIELDS
    products_used = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Product.objects.all(), required=False, write_only=True
    )
    payment_methods = serializers.PrimaryKeyRelatedField(
        many=True, queryset=PaymentMethod.objects.all(), required=False, write_only=True
    )
    social_links = SocialLinkSerializer(many=True, required=False, write_only=True)

    # Document fields...
    id_documents = serializers.PrimaryKeyRelatedField(many=True, queryset=Document.objects.all(), required=False, write_only=True)
    supporting_images = serializers.PrimaryKeyRelatedField(many=True, queryset=Document.objects.all(), required=False, write_only=True)
    profile_picture = serializers.PrimaryKeyRelatedField(queryset=Document.objects.all(), required=False, write_only=True)
    certifications = serializers.PrimaryKeyRelatedField(many=True, queryset=Document.objects.all(), required=False, write_only=True)

    # Read-only nested document data
    id_documents_data = serializers.SerializerMethodField()
    supporting_images_data = serializers.SerializerMethodField()
    profile_picture_data = serializers.SerializerMethodField()
    certifications_data = serializers.SerializerMethodField()

    # trial_paid_type field
    trial_paid_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # date_of_birth field - make it optional
    date_of_birth = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = ArtistProfile
        fields = ["id",
            'first_name', 'last_name', 'phone', 'email', 'gender', 'date_of_birth',
            'referel_code', 'offer_chosen', 'bio',
            'type_of_makeup', 'products_used', 'products_used_data',
            'payment_methods', 'payment_methods_data',
            'price_range', 'experience_years', 'services', 'services_offered', 'travel_charges',
            'travel_policy', 'trial_available', 'trial_paid_type', 'location',
            'social_links', 'social_links_data',
            'profile_picture', 'certifications', 'id_documents', 'supporting_images',
            'profile_picture_data', 'certifications_data',
            'id_documents_data', 'supporting_images_data',
            'average_rating', 'total_ratings', 'status', 'payment_status',
            'my_referral_code',
            # new: expose claimed leads count
            'my_claimed_leads',
            "created_by_admin",
            # new: current plan information
            'current_plan', 'plan_purchase_date', 'plan_verified',
            'available_leads',
            'extended_days',
        ]

    def to_internal_value(self, data):
        # Handle empty date_of_birth before validation
        if 'date_of_birth' in data:
            dob_value = data['date_of_birth']
            if dob_value in [None, '', 'null'] or (isinstance(dob_value, str) and dob_value.strip() == ''):
                data['date_of_birth'] = None
        return super().to_internal_value(data)

    def validate_date_of_birth(self, value):
        if value in [None, '', 'null']:
            return None
        if isinstance(value, str) and value.strip() == '':
            return None
        # If it's a valid date string, let Django handle the conversion
        return value


    def get_id_documents_data(self, obj):
        return DocumentSerializer(obj.id_documents.filter(is_active=True), many=True).data

    def get_supporting_images_data(self, obj):
        return DocumentSerializer(obj.supporting_images.filter(is_active=True), many=True).data

    def get_profile_picture_data(self, obj):
        if obj.profile_picture and obj.profile_picture.is_active:
            return DocumentSerializer(obj.profile_picture).data
        return None

    def get_certifications_data(self, obj):
        return DocumentSerializer(obj.certifications.filter(is_active=True), many=True).data

    def get_services_offered(self, obj):
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

    def validate_supporting_images(self, value):
        if len(value) > 8:
            raise serializers.ValidationError("You can upload a maximum of 8 supporting images.")
        return value

    def create(self, validated_data):
        social_links_data = validated_data.pop('social_links', [])
        artist = super().create(validated_data)
        self._update_social_links(artist, social_links_data)
        return artist

    def update(self, instance, validated_data):
        social_links_data = validated_data.pop('social_links', [])
        instance = super().update(instance, validated_data)
        self._update_social_links(instance, social_links_data)
        return instance

    def _update_social_links(self, artist, links_data):
        artist.social_links.all().delete()
        for link_data in links_data:
            SocialLink.objects.create(artist=artist, **link_data)


class AdminArtistProfileSerializer(serializers.ModelSerializer):
    user_phone = serializers.CharField(source="user.phone", read_only=True)
    location = LocationSerializer()
    type_of_makeup = MakeupTypeSerializer(many=True)
    products_used = ProductSerializer(many=True)
    payment_methods = PaymentMethodSerializer(many=True)
    social_links = SocialLinkSerializer(many=True)
    current_plan = SubscriptionPlanSerializer()
    
    # Document related fields
    profile_picture = serializers.SerializerMethodField()
    certifications = serializers.SerializerMethodField()
    id_documents = serializers.SerializerMethodField()
    supporting_images = serializers.SerializerMethodField()

    class Meta:
        model = ArtistProfile
        fields = [
            'id',
            'user_phone',
            # Personal Info
            'first_name',
            'last_name',
            'phone',
            'email',
            'gender',
            'date_of_birth',
            # Location
            'location',
            # Business Details
            'referel_code',
            'my_referral_code',
            'offer_chosen',
            'bio',
            'type_of_makeup',
            'price_range',
            'products_used',
            'experience_years',
            'payment_methods',
            'services',
            'travel_charges',
            'travel_policy',
            'trial_available',
            'trial_paid_type',
            'tag',
            # Social Links
            'social_links',
            # Documents
            'profile_picture',
            'certifications',
            'id_documents',
            'supporting_images',
            # Status and Metrics
            'payment_status',
            'status',
            'internal_notes',
            'average_rating',
            'total_ratings',
            'available_leads',
            'is_active',
            'my_claimed_leads',
            'total_bookings',
            # Plan Related
            'current_plan',
            'plan_purchase_date',
            'plan_verified',
            'extended_days',
            # Other
            'created_by_admin',
            'created_at'
        ]
    
    def get_profile_picture(self, obj):
        if obj.profile_picture:
            return DocumentSerializer(obj.profile_picture).data
        return None

    def get_certifications(self, obj):
        return DocumentSerializer(obj.certifications.all(), many=True).data

    def get_id_documents(self, obj):
        return DocumentSerializer(obj.id_documents.all(), many=True).data

    def get_supporting_images(self, obj):
        return DocumentSerializer(obj.supporting_images.all(), many=True).data


class ArtistSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtistSubscription
        fields = '__all__'

class PlanPurchaseSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField()

class ReferralCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtistProfile
        fields = ['my_referral_code']
        read_only_fields = ['my_referral_code']

class ArtistServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'price', 'credits']


from artists.models.models import ArtistActivityLog

class ArtistActivityLogSerializer(serializers.ModelSerializer):
    artist_name = serializers.CharField(source='artist.first_name', read_only=True)
    artist_phone = serializers.CharField(source='artist.phone', read_only=True)

    class Meta:
        model = ArtistActivityLog
        fields = [
            'id', 'activity_type', 'timestamp', 'leads_before', 'leads_after', 'details',
            'artist_name', 'artist_phone'
        ]
        read_only_fields = ['id', 'timestamp']
