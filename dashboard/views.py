from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.db.models import Avg
from dateutil.relativedelta import relativedelta 

class DashboardViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.request.user.transactions.all()
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get main dashboard summary"""
        transactions = self.get_queryset()
        
        total_income = transactions.filter(transaction_type='income').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        
        total_expenses = transactions.filter(transaction_type='expense').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        
        return Response({
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_balance': total_income - total_expenses,
            'total_transactions': transactions.count(),
            'average_transaction': transactions.aggregate(
            avg=Avg('amount')     # ← use Avg() which handles empty sets gracefully
            )['avg'] or 0,
        })
    
    @action(detail=False, methods=['get'])
    def category_breakdown(self, request):
        """Get breakdown by category"""
        transactions = self.get_queryset()
        
        income_by_category = transactions.filter(transaction_type='income')\
            .values('category')\
            .annotate(total=Sum('amount'))\
            .order_by('-total')
        
        expense_by_category = transactions.filter(transaction_type='expense')\
            .values('category')\
            .annotate(total=Sum('amount'))\
            .order_by('-total')
        
        return Response({
            'income': {item['category']: item['total'] for item in income_by_category},
            'expense': {item['category']: item['total'] for item in expense_by_category}
        })
    
    @action(detail=False, methods=['get'])
    def monthly_trends(self, request):
        """Get monthly trends for last 6 months"""
        transactions = self.get_queryset()
        months = int(request.query_params.get('months', 6))
        
        trends = []
        today = timezone.now().date()
        
        for i in range(months - 1, -1, -1):
            month_start = (today.replace(day=1) - relativedelta(months=i))
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)
            
            month_transactions = transactions.filter(
                date__gte=month_start, date__lte=month_end
            )
            
            income = month_transactions.filter(transaction_type='income').aggregate(
                Sum('amount')
            )['amount__sum'] or 0
            
            expenses = month_transactions.filter(transaction_type='expense').aggregate(
                Sum('amount')
            )['amount__sum'] or 0
            
            trends.append({
                'month': month_start.strftime('%B %Y'),
                'income': income,
                'expenses': expenses,
                'net': income - expenses,
                'transaction_count': month_transactions.count()
            })
        
        return Response(trends)
    
    @action(detail=False, methods=['get'])
    def recent_activity(self, request):
        """Get recent transactions"""
        limit = int(request.query_params.get('limit', 10))
        recent = self.get_queryset()[:limit]
        
        from records.serializers import TransactionSerializer
        serializer = TransactionSerializer(recent, many=True)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def financial_health(self, request):
        """Get financial health metrics"""
        transactions = self.get_queryset()
        
        total_income = transactions.filter(transaction_type='income').aggregate(
            Sum('amount')
        )['amount__sum'] or Decimal('0')
        
        total_expenses = transactions.filter(transaction_type='expense').aggregate(
            Sum('amount')
        )['amount__sum'] or Decimal('0')
        
        # Savings rate
        savings_rate = ((total_income - total_expenses) / total_income * 100) if total_income > 0 else 0
        
        # Top categories
        top_expense = transactions.filter(transaction_type='expense')\
            .values('category')\
            .annotate(total=Sum('amount'))\
            .order_by('-total')\
            .first()
        
        top_income = transactions.filter(transaction_type='income')\
            .values('category')\
            .annotate(total=Sum('amount'))\
            .order_by('-total')\
            .first()
        
        return Response({
            'savings_rate': round(savings_rate, 2),
            'expense_to_income_ratio': round(
                (total_expenses / total_income * 100) if total_income > 0 else 0, 2
            ),
            'top_expense_category': top_expense['category'] if top_expense else None,
            'top_expense_amount': top_expense['total'] if top_expense else 0,
            'top_income_category': top_income['category'] if top_income else None,
            'top_income_amount': top_income['total'] if top_income else 0,
            'daily_average_expense': total_expenses / 30 if total_expenses > 0 else 0
        })
