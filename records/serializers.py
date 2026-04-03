from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    formatted_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'user', 'user_name', 'amount', 'formatted_amount',
            'transaction_type', 'category', 'date', 'description',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_formatted_amount(self, obj):
        return f"${obj.amount:,.2f}"
    
    def validate(self, data):
        # Validate category based on transaction type
        transaction_type = data.get('transaction_type')
        category = data.get('category')
        
        valid_categories = dict(Transaction.CATEGORIES[transaction_type])
        
        if category not in valid_categories:
            raise serializers.ValidationError(
                f"Invalid category for {transaction_type}. "
                f"Valid categories: {', '.join(valid_categories.keys())}"
            )
        
        # Additional validation for large expenses
        if transaction_type == 'expense' and data.get('amount', 0) > 10000:
            raise serializers.ValidationError(
                {"amount": "Large expense (> $10,000) requires additional approval"}
            )
        
        return data

class TransactionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_type', 'category', 'date', 'description', 'notes']
    
    def validate(self, data):
        return super().validate(data)