from rest_framework import serializers
from .models import CreditTransaction, ArtistCreditBalance, CreditType
from adminpanel.serializers.subscriptions_serializers import SubscriptionPlanSerializer

class CreditTransactionSerializer(serializers.ModelSerializer):
    plan_details = SubscriptionPlanSerializer(source='subscription_plan', read_only=True)
    
    class Meta:
        model = CreditTransaction
        fields = [
            'id',
            'transaction_type',
            'credit_type',
            'credits_before',
            'credits_amount',
            'credits_after',
            'description',
            'reference_id',
            'subscription_plan',
            'plan_details',
            'created_at',
            'is_positive',
            'is_negative'
        ]
        read_only_fields = ['id', 'created_at', 'is_positive', 'is_negative']

class ArtistCreditBalanceSerializer(serializers.ModelSerializer):
    credit_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = ArtistCreditBalance
        fields = [
            'lead_credits',
            'premium_feature_credits',
            'boost_profile_credits',
            'total_lead_credits_earned',
            'total_premium_credits_earned',
            'total_boost_credits_earned',
            'total_lead_credits_consumed',
            'total_premium_credits_consumed',
            'total_boost_credits_consumed',
            'last_updated',
            'credit_summary'
        ]
    
    def get_credit_summary(self, obj):
        return obj.get_credit_summary()

# class CreditSummarySerializer(serializers.Serializer):
#     current_balance = ArtistCreditBalanceSerializer()
#     recent_transactions = CreditTransactionSerializer(many=True)
#     total_transactions = serializers.IntegerField()