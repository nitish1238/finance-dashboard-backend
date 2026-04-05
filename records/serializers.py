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
        read_only_fields = ['id', 'created_at', 'updated_at','user']
    
    def get_formatted_amount(self, obj):
        return f"${obj.amount:,.2f}"
    
    def validate(self, data):
        transaction_type = data.get('transaction_type')
        category = data.get('category')

    
        if transaction_type and category:
            category_dict = dict(Transaction.CATEGORIES)

        
            if transaction_type in category_dict:
                valid_categories = dict(category_dict[transaction_type])

            
                if category not in valid_categories:
                    raise serializers.ValidationError({
                        "category": f"{category} is not valid for {transaction_type}"
                    })

    
        if transaction_type == 'expense':
            amount = data.get('amount') or 0
            if float(amount) > 10000:
                raise serializers.ValidationError({
                    "amount": "Large expense (> 10000) not allowed"
                })

        return data
class TransactionCreateSerializer(TransactionSerializer):
    class Meta(TransactionSerializer.Meta):
        fields = ['amount', 'transaction_type', 'category', 'date', 'description', 'notes']
    
    