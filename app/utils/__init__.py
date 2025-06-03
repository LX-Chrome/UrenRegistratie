from datetime import datetime

def parse_date(date_str, default=None, fmt='%Y-%m-%d'):
    """Parse a date string safely, returning default if invalid"""
    if not date_str:
        return default
    try:
        return datetime.strptime(date_str, fmt).date()
    except ValueError:
        return default
        
def parse_float(value_str, default=None):
    """Parse a float value safely, returning default if invalid"""
    if not value_str or not value_str.strip():
        return default
    try:
        return float(value_str)
    except ValueError:
        return default
