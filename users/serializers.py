from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User
from artists.models.models import Location
from adminpanel.models import SubscriptionPlan

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        login_id = attrs.get("username")  # Allow phone or username
        password = attrs.get("password")

        user = (
            User.objects.filter(username=login_id).first() or
            User.objects.filter(phone=login_id).first()
        )

        if user is None:
            raise serializers.ValidationError("Invalid username or phone.")
        if not user.check_password(password):
            raise serializers.ValidationError("Incorrect password.")
        if not user.is_active:
            raise serializers.ValidationError("Account is inactive.")

        data = super().validate({"username": user.username, "password": password})
        data["user_id"] = user.id
        data["role"] = user.role
        return data

class AdminArtistSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=15)
    email = serializers.EmailField(required=False, allow_blank=True)
    gender = serializers.CharField(max_length=10, required=False, allow_blank=True)
    city = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=100)
    pincode = serializers.CharField(max_length=10, required=False, allow_blank=True, allow_null=True)
    lat = serializers.FloatField(required=False)
    lng = serializers.FloatField(required=False)
    available_leads = serializers.IntegerField(default=6)
    created_by_admin = serializers.BooleanField(default=True)
    subscription_plan_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Phone number already exists.")
        return value

    def validate_subscription_plan_id(self, value):
        if value:
            try:
                SubscriptionPlan.objects.get(id=value)
            except SubscriptionPlan.DoesNotExist:
                raise serializers.ValidationError("Invalid subscription plan ID.")
        return value
