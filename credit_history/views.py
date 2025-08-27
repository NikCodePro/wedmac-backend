from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

from .models import CreditTransaction, ArtistCreditBalance
from .serializers import (
    CreditTransactionSerializer, 
    ArtistCreditBalanceSerializer
)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class ArtistCreditBalanceView(APIView):
    """Get current credit balance for authenticated artist"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            artist = request.user.artist_profile
            credit_balance, created = ArtistCreditBalance.objects.get_or_create(artist=artist)
            serializer = ArtistCreditBalanceSerializer(credit_balance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ArtistCreditHistoryView(APIView):
    """Get credit transaction history for authenticated artist"""
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        try:
            artist = request.user.artist_profile
            
            # Build queryset
            queryset = CreditTransaction.objects.filter(artist=artist)
            
            # Apply filters
            transaction_type = request.query_params.get('type')
            credit_type = request.query_params.get('credit_type')
            date_from = request.query_params.get('date_from')
            date_to = request.query_params.get('date_to')
            
            if transaction_type:
                queryset = queryset.filter(transaction_type=transaction_type)
            
            if credit_type:
                queryset = queryset.filter(credit_type=credit_type)
            
            if date_from:
                queryset = queryset.filter(created_at__gte=date_from)
            
            if date_to:
                queryset = queryset.filter(created_at__lte=date_to)
            
            # Order by created_at descending
            queryset = queryset.order_by('-created_at')
            
            # Paginate results
            paginator = StandardResultsSetPagination()
            paginated_queryset = paginator.paginate_queryset(queryset, request)
            
            serializer = CreditTransactionSerializer(paginated_queryset, many=True)
            return paginator.get_paginated_response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
