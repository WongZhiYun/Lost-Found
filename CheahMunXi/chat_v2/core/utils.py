"""
Utility functions
"""
import re
from datetime import datetime


def format_timestamp(timestamp):
    """
    Format timestamp to friendly display
    
    Args:
        timestamp: datetime object
        
    Returns:
        str: Formatted timestamp string
    """
    now = datetime.now()
    
    if timestamp.date() == now.date():
        # Today: display time
        return timestamp.strftime('%H:%M')
    elif timestamp.date().year == now.year:
        # This year: display month and day
        return timestamp.strftime('%d/%m')
    else:
        # Other years: display year, month and day
        return timestamp.strftime('%d/%m/%y')


def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email address
        
    Returns:
        bool: Whether valid
    """
    # Simple regex for basic email validation
    email_regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    return bool(re.match(email_regex, email))


def truncate_message(message: str, max_length: int = 50) -> str:
    """
    Truncate long message
    
    Args:
        message: Original message
        max_length: Maximum length
        
    Returns:
        str: Truncated message
    """
    if len(message) <= max_length:
        return message
    return message[:max_length] + '...'


def safe_str(obj) -> str:
    """
    Safely convert object to string
    
    Args:
        obj: Any object
        
    Returns:
        str: String representation
    """
    try:
        return str(obj) if obj is not None else ''
    except Exception:
        # If conversion raises an error, return empty string
        return ''
