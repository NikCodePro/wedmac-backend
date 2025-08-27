from rest_framework import serializers
from .models import Rating

class RatingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'artist', 'rating', 'description']

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

