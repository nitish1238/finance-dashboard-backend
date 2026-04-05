from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum
from .models import Transaction
from .serializers import TransactionSerializer


class TransactionViewSet(ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    
    def get_queryset(self):
        user = self.request.user

    
        if not user.is_authenticated:
            return Transaction.objects.none()

    
        if getattr(user, "role", None) == 'admin':
            queryset = Transaction.objects.all()
        else:
            queryset = Transaction.objects.filter(user=user)

    
        category = self.request.query_params.get('category')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        search = self.request.query_params.get('search')
        min_amount = self.request.query_params.get('min_amount')
        max_amount = self.request.query_params.get('max_amount')
        transaction_type = self.request.query_params.get('transaction_type')

        if category:
            queryset = queryset.filter(category=category)

        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])

        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)

        if min_amount:
            queryset = queryset.filter(amount__gte=min_amount)

        if max_amount:
            queryset = queryset.filter(amount__lte=max_amount)

        if search:
            queryset = queryset.filter(
                Q(description__icontains=search) |
                Q(notes__icontains=search)
            )

        return queryset

   
    def create(self, request, *args, **kwargs):
        if request.user.role == 'viewer':
            raise PermissionDenied("Viewer cannot create")

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if request.user.role == 'viewer':
            raise PermissionDenied("Viewer cannot update")

        if request.user.role == 'analyst' and instance.user != request.user:
            raise PermissionDenied("Not allowed")

        return super().update(request, *args, **kwargs)

    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if request.user.role == 'viewer':
            raise PermissionDenied("Viewer cannot delete")

        if request.user.role == 'analyst':
            raise PermissionDenied("Analyst cannot delete")

        return super().destroy(request, *args, **kwargs)

    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        queryset = self.get_queryset()

        income = queryset.filter(transaction_type='income').aggregate(
            total=Sum('amount')
        )['total'] or 0

        expense = queryset.filter(transaction_type='expense').aggregate(
            total=Sum('amount')
        )['total'] or 0

        return Response({
            "total_income": {"total": income},
            "total_expense": {"total": expense},
            "net_balance": income - expense   
        })

    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        category_dict = dict(Transaction.CATEGORIES)

        return Response({
            'income': dict(category_dict.get('income', [])),
            'expense': dict(category_dict.get('expense', []))
        })
