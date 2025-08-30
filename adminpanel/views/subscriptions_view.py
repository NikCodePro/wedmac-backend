from rest_framework import generics
from adminpanel.models import SubscriptionPlan
from adminpanel.serializers.subscriptions_serializers import SubscriptionPlanSerializer
from rest_framework import generics, permissions
from adminpanel.models import SubscriptionPlan
from adminpanel.serializers.subscriptions_serializers import CreateSubscriptionPlanSerializer
from rest_framework.permissions import IsAuthenticated
from superadmin_auth.permissions import IsSuperAdmin
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from uuid import UUID

class CreateSubscriptionPlanView(generics.CreateAPIView):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = CreateSubscriptionPlanSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admin can create

class SubscriptionPlanListView(generics.ListAPIView):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer

class UpdateSubscriptionPlanView(APIView):
    permission_classes = [IsSuperAdmin]

    def _get_plan(self, plan_id):
        # accept hyphenated or non-hyphenated UUID strings
        try:
            plan_uuid = UUID(plan_id)
            return get_object_or_404(SubscriptionPlan, id=plan_uuid)
        except Exception:
            # fallback: try raw string (if stored as hex/text)
            return get_object_or_404(SubscriptionPlan, id=plan_id)

    def put(self, request, plan_id):
        plan = self._get_plan(plan_id)
        serializer = CreateSubscriptionPlanSerializer(plan, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, plan_id):
        return self.put(request, plan_id)

class DeleteSubscriptionPlanView(APIView):
    permission_classes = [IsSuperAdmin]

    def delete(self, request, plan_id):
        plan = UpdateSubscriptionPlanView()._get_plan(plan_id)
        plan.delete()
        return Response({"message": "Subscription plan deleted", "id": str(plan_id)}, status=status.HTTP_200_OK)
