from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from superadmin_auth.permissions import IsSuperAdmin
from django.shortcuts import get_object_or_404

from adminpanel.models import PaymentMethod, Product, Service, BudgetRange, MakeupType, SubscriptionPlan
from adminpanel.serializers.subscriptions_serializers import SubscriptionPlanSerializer

# Import your existing serializers from get_master_lists.py
from adminpanel.views.get_master_list import (
    ServiceSerializer, 
    BudgetRangeSerializer, 
    MakeupTypeSerializer, 
    ProductSerializer, 
    paymentMethodSerializer
)

# Map type values to their model and serializer
TYPE_CREATE_MAP = {
    'services': (Service, ServiceSerializer),
    'budgets': (BudgetRange, BudgetRangeSerializer),
    'makeup_types': (MakeupType, MakeupTypeSerializer),
    # 'subscriptions_plan': (SubscriptionPlan, SubscriptionPlanSerializer),
    'products': (Product, ProductSerializer),
    'payment_methods': (PaymentMethod, paymentMethodSerializer),
}

def _validate_type_parameter(request):
    """Helper function to validate type parameter"""
    data_type = request.query_params.get('type', '').strip().lower()
    
    if not data_type:
        return None, Response({
            "error": "Missing 'type' parameter. Use one of: " + ", ".join(TYPE_CREATE_MAP.keys())
        }, status=status.HTTP_400_BAD_REQUEST)
    
    handler = TYPE_CREATE_MAP.get(data_type)
    if not handler:
        return None, Response({
            "error": f"Invalid type '{data_type}'. Use one of: " + ", ".join(TYPE_CREATE_MAP.keys())
        }, status=status.HTTP_400_BAD_REQUEST)
    
    return data_type, None

class CreateMasterDataAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]  # Only admin can create
    
    def post(self, request):
        data_type, error_response = _validate_type_parameter(request)
        if error_response:
            return error_response
        
        model_class, serializer_class = TYPE_CREATE_MAP[data_type]
        
        # Check if request data is a list (bulk create) or single object
        is_bulk = isinstance(request.data, list)
        
        serializer = serializer_class(data=request.data, many=is_bulk)
        
        if serializer.is_valid():
            instances = serializer.save()
            
            if is_bulk:
                return Response({
                    "message": f"Successfully created {len(instances)} {data_type} records",
                    "created_count": len(instances),
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "message": f"Successfully created {data_type} record",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
        
        return Response({
            "error": "Validation failed",
            "details": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class UpdateMasterDataAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    
    def put(self, request):
        """Full update - all fields required"""
        data_type, error_response = _validate_type_parameter(request)
        if error_response:
            return error_response
        
        model_class, serializer_class = TYPE_CREATE_MAP[data_type]
        
        # Get ID from request body
        obj_id = request.data.get('id')
        if not obj_id:
            return Response({
                "error": "Field 'id' is required in request body"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the instance
        try:
            instance = get_object_or_404(model_class, pk=obj_id)
        except:
            return Response({
                "error": f"Record with id '{obj_id}' not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Update with full data (partial=False)
        serializer = serializer_class(instance, data=request.data, partial=False)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": f"Successfully updated {data_type} record",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            "error": "Validation failed",
            "details": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        """Partial update - only provided fields updated"""
        data_type, error_response = _validate_type_parameter(request)
        if error_response:
            return error_response
        
        model_class, serializer_class = TYPE_CREATE_MAP[data_type]
        
        # Get ID from request body
        obj_id = request.data.get('id')
        if not obj_id:
            return Response({
                "error": "Field 'id' is required in request body"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the instance
        try:
            instance = get_object_or_404(model_class, pk=obj_id)
        except:
            return Response({
                "error": f"Record with id '{obj_id}' not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Update with partial data (partial=True)
        serializer = serializer_class(instance, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": f"Successfully updated {data_type} record",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            "error": "Validation failed",
            "details": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class DeleteMasterDataAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    
    def delete(self, request):
        data_type, error_response = _validate_type_parameter(request)
        if error_response:
            return error_response
        
        model_class, serializer_class = TYPE_CREATE_MAP[data_type]
        
        # Option 1: Single delete via query parameter
        obj_id = request.query_params.get('id')
        if obj_id:
            try:
                instance = get_object_or_404(model_class, pk=obj_id)
                instance.delete()
                return Response({
                    "message": f"Successfully deleted {data_type} record",
                    "deleted_id": obj_id
                }, status=status.HTTP_200_OK)
            except:
                return Response({
                    "error": f"Record with id '{obj_id}' not found"
                }, status=status.HTTP_404_NOT_FOUND)
        
        # Option 2: Bulk delete via request body
        ids = request.data.get('ids')
        if isinstance(ids, list) and ids:
            try:
                # Filter records that exist
                existing_records = model_class.objects.filter(pk__in=ids)
                deleted_count = existing_records.count()
                
                if deleted_count == 0:
                    return Response({
                        "error": "No records found with provided IDs"
                    }, status=status.HTTP_404_NOT_FOUND)
                
                # Delete the records
                existing_records.delete()
                
                return Response({
                    "message": f"Successfully deleted {deleted_count} {data_type} records",
                    "deleted_count": deleted_count,
                    "requested_ids": ids
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    "error": f"Error deleting records: {str(e)}"
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Option 3: Single delete via request body
        single_id = request.data.get('id')
        if single_id:
            try:
                instance = get_object_or_404(model_class, pk=single_id)
                instance.delete()
                return Response({
                    "message": f"Successfully deleted {data_type} record",
                    "deleted_id": single_id
                }, status=status.HTTP_200_OK)
            except:
                return Response({
                    "error": f"Record with id '{single_id}' not found"
                }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            "error": "Provide 'id' in query params (?id=123) or request body {'id': 123} for single delete, or {'ids': [1,2,3]} for bulk delete"
        }, status=status.HTTP_400_BAD_REQUEST)
