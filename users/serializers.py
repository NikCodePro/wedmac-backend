# users/serializers.py

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User

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
