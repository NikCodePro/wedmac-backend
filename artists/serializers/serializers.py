from rest_framework import serializers
from artists.models.models import ArtistProfile, ArtistSubscription, SocialLink
from documents.models import Document
from adminpanel.models import MakeupType, Product, PaymentMethod
from artists.models.models import Location 
from adminpanel.models import Service
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


# Main ArtistProfile Serializer
class ArtistProfileSerializer(serializers.ModelSerializer):
    # READ FIELDS
    type_of_makeup = MakeupTypeSerializer(many=True, read_only=True)
    products_used_data = ProductSerializer(source='products_used', many=True, read_only=True)
    payment_methods_data = PaymentMethodSerializer(source='payment_methods', many=True, read_only=True)
    social_links_data = SocialLinkSerializer(source='social_links', many=True, read_only=True)

    location = LocationSerializer(read_only=True)

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

    class Meta:
        model = ArtistProfile
        fields = [
            'first_name', 'last_name', 'phone', 'email', 'gender', 'date_of_birth',
            'referel_code', 'offer_chosen', 'bio',
            'type_of_makeup', 'products_used', 'products_used_data',
            'payment_methods', 'payment_methods_data',
            'price_range', 'experience_years', 'services', 'travel_charges',
            'travel_policy', 'trial_available', 'trial_paid_type', 'location',
            'social_links', 'social_links_data',
            'profile_picture', 'certifications', 'id_documents', 'supporting_images',
            'profile_picture_data', 'certifications_data',
            'id_documents_data', 'supporting_images_data',
            'average_rating', 'total_ratings', 'status', 'payment_status',
            'my_referral_code',
            # new: expose claimed leads count
            'my_claimed_leads',
        ]


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
    location = serializers.StringRelatedField()
    profile_picture = serializers.SerializerMethodField()
    certifications = serializers.SerializerMethodField()

    class Meta:
        model = ArtistProfile
        fields = [
            "id",
            "user_phone",
            "first_name", "last_name",
            "phone", "email",
            "gender", "date_of_birth",
            "location",
            "payment_status", "status",
            "internal_notes",
            "profile_picture",
            "certifications",
            "created_at",
            'my_referral_code',
            "bio",
            "type_of_makeup",
            "price_range",
            "experience_years",
            "services",
            "profile_picture",
            "certifications",
            "id_documents",
            "is_active",
            # new
            "my_claimed_leads",
        ]

    def get_profile_picture(self, obj):
        if obj.profile_picture:
            return DocumentSerializer(obj.profile_picture).data
        return None

    def get_certifications(self, obj):
        return DocumentSerializer(obj.certifications.all(), many=True).data


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