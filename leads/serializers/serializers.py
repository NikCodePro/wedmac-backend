from rest_framework import serializers
from leads.models.models import Lead
from adminpanel.models import BudgetRange, MakeupType, Service
from artists.models import ArtistProfile, Location
from users.models import User

class NestedServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'description']

class NestedBudgetRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetRange
        fields = ['id', 'label', 'min_value', 'max_value']

class NestedMakeupTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MakeupType
        fields = ['id', 'name', 'description']

class NestedLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'city', 'state', 'pincode']


class LeadSerializer(serializers.ModelSerializer):
    makeup_types = NestedMakeupTypeSerializer(many=True, read_only=True)
    budget_range = NestedBudgetRangeSerializer(read_only=True)
    service = NestedServiceSerializer(read_only=True)
    location = NestedLocationSerializer(read_only=True)
    claimed_artists = serializers.PrimaryKeyRelatedField(
        many=True, queryset=ArtistProfile.objects.all(), required=False
    )
    booked_artists = serializers.PrimaryKeyRelatedField(
        many=True, queryset=ArtistProfile.objects.all(), required=False
    )
    claimed_count = serializers.SerializerMethodField()
    booked_count = serializers.SerializerMethodField()
    max_claims = serializers.IntegerField(required=False)


    class Meta:
        model = Lead
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def get_claimed_count(self, obj):
        return obj.claimed_artists.count()

    def get_booked_count(self, obj):
        return obj.booked_artists.count()

# this serializer is used for the recent leads list for artist dashboard
class LeadDashboardListSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()
    service = serializers.CharField(source='service.name', read_only=True, default='N/A')
    location = serializers.CharField(source='location.city', read_only=True, default='N/A')
    budget_range = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = ['id', 'client_name', 'status', 'service', 'booking_date', 'location', 'requirements', 'budget_range', 'phone']

    def get_client_name(self, obj):
        return f"{obj.first_name or ''} {obj.last_name or ''}".strip()

    def get_budget_range(self, obj):
        br = getattr(obj, 'budget_range', None)
        if not br:
            return None
        return {
            'id': br.id,
            'label': getattr(br, 'label', None),
            'min_value': getattr(br, 'min_value', None),
            'max_value': getattr(br, 'max_value', None),
        }

# This is your nested serializer for lead detail view

class NestedArtistProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtistProfile
        fields = ['id', 'first_name','last_name','phone']

class NestedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone']

# 🆕 This is your nested serializer for lead detail view
class LeadDetailSerializer(serializers.ModelSerializer):
    service = NestedServiceSerializer(read_only=True)
    budget_range = NestedBudgetRangeSerializer(read_only=True)
    makeup_types = NestedMakeupTypeSerializer(read_only=True, many=True)
    location = NestedLocationSerializer(read_only=True)
    assigned_to = NestedArtistProfileSerializer(read_only=True)
    requested_artist = NestedArtistProfileSerializer(read_only=True)
    created_by = NestedUserSerializer(read_only=True)
    claimed_artists = NestedArtistProfileSerializer(read_only=True, many=True)
    booked_artists = NestedArtistProfileSerializer(read_only=True, many=True)
    claimed_count = serializers.SerializerMethodField()
    booked_count = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = '__all__'

    def get_claimed_count(self, obj):
        return obj.claimed_artists.count()

    def get_booked_count(self, obj):
        return obj.booked_artists.count()

# This serializer is used for the claimed leads list for artist dashboard


class MakeupTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MakeupType
        fields = ['id', 'name']

class ClaimedLeadListSerializer(serializers.ModelSerializer):
    makeup_types = MakeupTypeSerializer(many=True, read_only=True)
    service = serializers.StringRelatedField()
    budget_range = serializers.StringRelatedField()
    location = serializers.StringRelatedField()
    assigned_to = serializers.StringRelatedField()
    requested_artist = serializers.StringRelatedField()
    claimed_count = serializers.SerializerMethodField()
    booked_count = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = [
            'id', 'makeup_types', 'first_name', 'last_name', 'phone', 'email',
            'event_type', 'requirements', 'booking_date', 'source', 'status',
            'last_contact', 'notes', 'created_at', 'updated_at',
            'service', 'budget_range', 'location',
            'assigned_to', 'requested_artist', 'created_by',
            'claimed_count', 'booked_count'
        ]

    def get_claimed_count(self, obj):
        return obj.claimed_artists.count()

    def get_booked_count(self, obj):
        return obj.booked_artists.count()
