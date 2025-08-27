from django import forms
from django.contrib import admin
from .models import BudgetRange, MakeupType, PaymentMethod, Product, Service, SubscriptionPlan

FEATURE_CHOICES = [
    ("Profile Boost", "Profile Boost"),
    ("Priority Support", "Priority Support"),
    ("Home Page Highlight", "Home Page Highlight"),
    ("Faster Lead Access", "Faster Lead Access"),
]

class SubscriptionPlanForm(forms.ModelForm):
    features = forms.MultipleChoiceField(
        choices=FEATURE_CHOICES,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = SubscriptionPlan
        fields = '__all__'

    def clean_features(self):
        return self.cleaned_data['features']  # will save as list

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    form = SubscriptionPlanForm
    list_display = ('name', 'price', 'total_leads', 'duration_days')
    readonly_fields = ('id',)
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('id',)
        return self.readonly_fields

admin.site.register(Service)
admin.site.register(BudgetRange)
admin.site.register(MakeupType)
admin.site.register(PaymentMethod)
admin.site.register(Product)

