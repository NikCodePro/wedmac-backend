from rest_framework import serializers
from leads.models.models import Lead
from adminpanel.models import MakeupType, Service
from artists.models.models import ArtistProfile, Location
from users.models import User

# This is your nested serializer for lead detail view

class NestedArtistProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtistProfile
        fields = ['id', 'first_name','last_name','phone']

class NestedServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'description']



class NestedMakeupTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MakeupType
        fields = ['id', 'name', 'description']

class NestedLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'city', 'state', 'pincode']


class MakeupTypeNameField(serializers.Field):
    """
    Custom field to handle makeup_types as names during input,
    but convert to MakeupType instances for storage.
    """

    def to_internal_value(self, data):
        if not isinstance(data, list):
            raise serializers.ValidationError("Makeup types must be a list of names or IDs.")

        makeup_type_instances = []
        for name in data:
            # Accept both string names and integer IDs
            if isinstance(name, int):
                try:
                    makeup_type = MakeupType.objects.get(id=name)
                    makeup_type_instances.append(makeup_type)
                except MakeupType.DoesNotExist:
                    raise serializers.ValidationError(f"Makeup type with ID '{name}' does not exist.")
            elif isinstance(name, str):
                try:
                    makeup_type = MakeupType.objects.get(name__iexact=name.strip())
                    makeup_type_instances.append(makeup_type)
                except MakeupType.DoesNotExist:
                    raise serializers.ValidationError(f"Makeup type '{name}' does not exist.")
            else:
                raise serializers.ValidationError(f"Makeup type name must be a string or int, got {type(name)}: {name}")

        return makeup_type_instances

    def to_representation(self, value):
        # This will be handled by the NestedMakeupTypeSerializer in to_representation
        return value





class LeadSerializer(serializers.ModelSerializer):
    makeup_types = MakeupTypeNameField(required=False)
    budget = serializers.IntegerField(required=False)
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), required=False)
    location = serializers.CharField(required=False)
    claimed_artists = NestedArtistProfileSerializer(read_only=True, many=True)
    booked_artists = NestedArtistProfileSerializer(read_only=True, many=True)
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=ArtistProfile.objects.all(), required=False, allow_null=True)
    requested_artist = serializers.PrimaryKeyRelatedField(queryset=ArtistProfile.objects.all(), required=False, allow_null=True)
    claimed_count = serializers.SerializerMethodField()
    booked_count = serializers.SerializerMethodField()
    max_claims = serializers.IntegerField(required=False)
    event_type = serializers.ChoiceField(choices=Lead.EVENT_CHOICES, required=False, allow_blank=True)


    class Meta:
        model = Lead
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.service:
            data['service'] = NestedServiceSerializer(instance.service).data
        if instance.assigned_to:
            data['assigned_to'] = NestedArtistProfileSerializer(instance.assigned_to).data
        if instance.requested_artist:
            data['requested_artist'] = NestedArtistProfileSerializer(instance.requested_artist).data

        # Handle makeup_types - convert to nested serializer format for response
        if hasattr(instance, 'makeup_types') and instance.makeup_types.exists():
            data['makeup_types'] = NestedMakeupTypeSerializer(instance.makeup_types.all(), many=True).data
        else:
            data['makeup_types'] = []

        return data

    def get_claimed_count(self, obj):
        return obj.claimed_artists.count()

    def get_booked_count(self, obj):
        return obj.booked_artists.count()

    def create(self, validated_data):
        makeup_types = validated_data.pop('makeup_types', [])
        lead = super().create(validated_data)

        # Add makeup types to the lead
        if makeup_types:
            lead.makeup_types.set(makeup_types)

        return lead

# this serializer is used for the recent leads list for artist dashboard
class LeadDashboardListSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()
    service = serializers.SerializerMethodField()
    location = serializers.CharField(read_only=True)
    budget = serializers.IntegerField(read_only=True)

    class Meta:
        model = Lead
        fields = ['id', 'client_name', 'status', 'service', 'booking_date', 'location', 'requirements', 'budget', 'phone', 'is_verified']

    def get_client_name(self, obj):
        return f"{obj.first_name or ''} {obj.last_name or ''}".strip()

    def get_service(self, obj):
        if obj.service:
            return obj.service.name
        return 'N/A'

class NestedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone']

# 🆕 This is your nested serializer for lead detail view
class LeadDetailSerializer(serializers.ModelSerializer):
    service = NestedServiceSerializer(read_only=True)
    budget = serializers.IntegerField(read_only=True)
    makeup_types = NestedMakeupTypeSerializer(read_only=True, many=True)
    location = NestedLocationSerializer(read_only=True)
    assigned_to = NestedArtistProfileSerializer(read_only=True)
    requested_artist = NestedArtistProfileSerializer(read_only=True)
    created_by = NestedUserSerializer(read_only=True)
    claimed_artists = NestedArtistProfileSerializer(read_only=True, many=True)
    booked_artists = NestedArtistProfileSerializer(read_only=True, many=True)
    claimed_count = serializers.SerializerMethodField()
    booked_count = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)

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
    budget = serializers.IntegerField(read_only=True)
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
            'service', 'budget', 'location',
            'assigned_to', 'requested_artist', 'created_by',
            'claimed_count', 'booked_count', 'is_verified'
        ]

    def get_claimed_count(self, obj):
        return obj.claimed_artists.count()

    def get_booked_count(self, obj):
        return obj.booked_artists.count()
