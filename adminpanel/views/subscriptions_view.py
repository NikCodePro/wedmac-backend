from rest_framework import generics
from adminpanel.models import SubscriptionPlan
from adminpanel.serializers.subscriptions_serializers import SubscriptionPlanSerializer
from rest_framework import generics, permissions
from adminpanel.models import SubscriptionPlan
from adminpanel.serializers.subscriptions_serializers import CreateSubscriptionPlanSerializer


class CreateSubscriptionPlanView(generics.CreateAPIView):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = CreateSubscriptionPlanSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admin can create

class SubscriptionPlanListView(generics.ListAPIView):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
 