from django.contrib import admin
from .models import CreditTransaction, ArtistCreditBalance, CreditType

@admin.register(ArtistCreditBalance)
class ArtistCreditBalanceAdmin(admin.ModelAdmin):
    list_display = [
        'artist', 
        'lead_credits', 
        'premium_feature_credits', 
        'boost_profile_credits',
        'last_updated'
    ]
    list_filter = ['last_updated']
    search_fields = ['artist__first_name', 'artist__last_name', 'artist__user__phone']
    readonly_fields = ['created_at', 'last_updated']

@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'artist',
        'transaction_type',
        'credit_type',
        'credits_amount',
        'credits_before',
        'credits_after',
        'created_at'
    ]
    list_filter = [
        'transaction_type', 
        'credit_type', 
        'created_at'
    ]
    search_fields = [
        'artist__first_name', 
        'artist__last_name', 
        'artist__user__phone',
        'description',
        'reference_id'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'