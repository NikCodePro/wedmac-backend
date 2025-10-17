from rest_framework import serializers
from adminpanel.models import SubscriptionPlan, Service
# adminpanel/views/subscription_views.py
# adminpanel/serializers/subscriptions_serializers.py


class CreateSubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['name', 'total_leads', 'price', 'duration_days', 'description', 'features', 'total_credit_points', 'claim_amount_limit']

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id',
            'name',
            'total_leads',
            'total_credit_points',
            'price',
            'duration_days',
            'description',
            'features',
            'claim_amount_limit',
            'created_at',
        ]
        
class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'
    
    def validate_price(self, value):
        """Ensure price is not negative"""
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative")
        return value