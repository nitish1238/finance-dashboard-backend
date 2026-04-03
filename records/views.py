from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Transaction
from .serializers import TransactionSerializer, TransactionCreateSerializer
from .filters import TransactionFilter
from core.permissions import RoleBasedPermission

class TransactionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TransactionFilter
    search_fields = ['description', 'notes']
    ordering_fields = ['amount', 'date', 'created_at']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin:
            return Transaction.objects.all()
        else:
            return Transaction.objects.filter(user=user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TransactionCreateSerializer
        return TransactionSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get all available categories"""
        return Response({
            'income': dict(Transaction.CATEGORIES['income']),
            'expense': dict(Transaction.CATEGORIES['expense'])
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get transaction statistics"""
        from django.db.models import Sum, Count, Avg
        
        queryset = self.get_queryset()
        
        stats = {
            'total_income': queryset.filter(transaction_type='income').aggregate(
                total=Sum('amount'), count=Count('id'), avg=Avg('amount')
            ),
            'total_expense': queryset.filter(transaction_type='expense').aggregate(
                total=Sum('amount'), count=Count('id'), avg=Avg('amount')
            ),
        }
        
        # Format response
        for key in ['total_income', 'total_expense']:
            stats[key]['total'] = stats[key]['total'] or 0
            stats[key]['avg'] = stats[key]['avg'] or 0
        
        stats['net_balance'] = stats['total_income']['total'] - stats['total_expense']['total']
        
        return Response(stats)
