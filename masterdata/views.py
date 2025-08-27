from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.permissions import AllowAny

from adminpanel.models import PaymentMethod, Product, Service, BudgetRange, MakeupType, SubscriptionPlan
from adminpanel.serializers.subscriptions_serializers import SubscriptionPlanSerializer
from artists.models.models import ArtistProfile
from leads.models.models import Lead

# Define serializers
class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class BudgetRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetRange
        fields = '__all__'

class MakeupTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MakeupType
        fields = '__all__'
class ArtistProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtistProfile  # Replace with actual model
        fields = ['id','first_name', 'last_name', 'phone', 'email',]
class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead  # Replace with actual model
        fields = ['id', 'first_name', 'last_name', 'phone', 'email', 'requested_artist']
        
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = '__all__'
# Map type values to their queryset and serializer
TYPE_SERIALIZER_MAP = {
    'services': (Service.objects.all, ServiceSerializer),
    'budgets': (BudgetRange.objects.all, BudgetRangeSerializer),
    'makeup_types': (MakeupType.objects.all, MakeupTypeSerializer),
    'subscriptions_plan': (SubscriptionPlan.objects.all, SubscriptionPlanSerializer),
    'artist': (ArtistProfile.objects.all, ArtistProfileSerializer),
    'leads': (Lead.objects.all, LeadSerializer),
    'products': (Product.objects.all, ProductSerializer),
    'payment_methods': (PaymentMethod.objects.all, PaymentMethodSerializer),
}

class MasterDataListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        data_type = request.query_params.get('type', '')
        data_type = data_type.strip().lower()
        print(f"Fetching master data for type: {repr(data_type)}")

        if not data_type:
            return Response({
                "error": "Missing 'type' parameter. Use one of: " + ", ".join(TYPE_SERIALIZER_MAP.keys())
            }, status=status.HTTP_400_BAD_REQUEST)

        data_type = data_type.strip().lower()

        # Get handler from the map
        handler = TYPE_SERIALIZER_MAP.get(data_type)

        if not handler:
            return Response({
                "error": f"Invalid type '{data_type}'. Use one of: " + ", ".join(TYPE_SERIALIZER_MAP.keys())
            }, status=status.HTTP_400_BAD_REQUEST)

        queryset_fn, serializer_class = handler
        items = queryset_fn()
        serializer = serializer_class(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
