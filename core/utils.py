from decimal import Decimal
from datetime import datetime, date
import json

class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder for Decimal objects"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:,.2f}"

def calculate_percentage(part, whole):
    """Calculate percentage"""
    if whole == 0:
        return 0
    return round((part / whole) * 100, 2)