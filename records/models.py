from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from users.models import User

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    
    CATEGORIES = {
        'income': [
            ('salary', 'Salary'),
            ('freelance', 'Freelance'),
            ('investment', 'Investment'),
            ('business', 'Business'),
            ('gift', 'Gift'),
            ('other_income', 'Other Income'),
        ],
        'expense': [
            ('food', 'Food & Dining'),
            ('transport', 'Transportation'),
            ('utilities', 'Utilities'),
            ('rent', 'Rent'),
            ('entertainment', 'Entertainment'),
            ('healthcare', 'Healthcare'),
            ('shopping', 'Shopping'),
            ('education', 'Education'),
            ('other_expense', 'Other Expense'),
        ]
    }
    
    # Flatten categories for choices
    CATEGORY_CHOICES = sum([cats for cats in CATEGORIES.values()], [])
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)]
    )
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'transactions'
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'transaction_type']),
            models.Index(fields=['user', 'category']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.transaction_type}: ${self.amount}"