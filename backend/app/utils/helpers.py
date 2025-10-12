"""
Utility Helper Functions
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, date, timedelta
import logging

logger = logging.getLogger(__name__)


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """Validate geographic coordinates"""
    return -90 <= latitude <= 90 and -180 <= longitude <= 180


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two points in kilometers using Haversine formula
    """
    from math import radians, cos, sin, asin, sqrt
    
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    
    return c * r


def format_date_range(start_date: date, end_date: date) -> str:
    """Format date range for display"""
    return f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"


def get_date_range(days_back: int) -> tuple:
    """Get start and end dates for a period"""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days_back)
    return start_date, end_date


def round_float(value: Optional[float], decimals: int = 2) -> Optional[float]:
    """Safely round float values"""
    if value is None:
        return None
    return round(value, decimals)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers"""
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max"""
    return max(min_val, min(value, max_val))


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values"""
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / old_value) * 100


def interpolate_value(x: float, x0: float, x1: float, y0: float, y1: float) -> float:
    """Linear interpolation"""
    if x1 == x0:
        return y0
    return y0 + (x - x0) * (y1 - y0) / (x1 - x0)


def moving_average(data: List[float], window: int) -> List[float]:
    """Calculate moving average"""
    if not data or window <= 0:
        return data
    
    result = []
    for i in range(len(data)):
        start = max(0, i - window + 1)
        window_data = data[start:i+1]
        result.append(sum(window_data) / len(window_data))
    
    return result


def classify_value(value: float, thresholds: Dict[str, float]) -> str:
    """
    Classify a value based on thresholds
    
    Example:
        thresholds = {'low': 30, 'medium': 60, 'high': 80}
        classify_value(45, thresholds) -> 'medium'
    """
    sorted_thresholds = sorted(thresholds.items(), key=lambda x: x[1])
    
    for label, threshold in sorted_thresholds:
        if value < threshold:
            return label
    
    return sorted_thresholds[-1][0]


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency value"""
    return f"{currency} {amount:,.2f}"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def parse_iso_date(date_string: str) -> Optional[date]:
    """Parse ISO format date string"""
    try:
        return datetime.fromisoformat(date_string).date()
    except (ValueError, AttributeError):
        return None


def get_season(date_obj: date) -> str:
    """Determine season from date (Kenya context)"""
    month = date_obj.month
    
    if month in [3, 4, 5]:
        return "Long Rains"
    elif month in [6, 7, 8, 9]:
        return "Dry Season"
    elif month in [10, 11, 12]:
        return "Short Rains"
    else:  # [1, 2]
        return "Dry Season"


def aggregate_by_period(data: List[Dict], date_field: str, value_field: str, period: str = "month") -> Dict:
    """
    Aggregate data by time period
    
    Args:
        data: List of dictionaries with date and value fields
        date_field: Name of date field
        value_field: Name of value field to aggregate
        period: 'day', 'week', 'month', or 'year'
    """
    from collections import defaultdict
    
    aggregated = defaultdict(list)
    
    for item in data:
        date_val = item.get(date_field)
        value = item.get(value_field)
        
        if not date_val or value is None:
            continue
        
        # Parse date if string
        if isinstance(date_val, str):
            date_val = parse_iso_date(date_val)
        
        # Determine period key
        if period == "day":
            key = date_val.isoformat()
        elif period == "week":
            key = f"{date_val.year}-W{date_val.isocalendar()[1]:02d}"
        elif period == "month":
            key = f"{date_val.year}-{date_val.month:02d}"
        elif period == "year":
            key = str(date_val.year)
        else:
            key = date_val.isoformat()
        
        aggregated[key].append(value)
    
    # Calculate averages
    result = {}
    for key, values in aggregated.items():
        result[key] = {
            'count': len(values),
            'sum': sum(values),
            'avg': sum(values) / len(values),
            'min': min(values),
            'max': max(values)
        }
    
    return result


def generate_color_from_value(value: float, min_val: float = 0, max_val: float = 100) -> str:
    """
    Generate color code based on value (green to red)
    
    Returns hex color code
    """
    # Normalize value to 0-1
    normalized = clamp((value - min_val) / (max_val - min_val), 0, 1)
    
    # Green (low) to Red (high)
    if normalized < 0.5:
        # Green to Yellow
        r = int(255 * (normalized * 2))
        g = 255
    else:
        # Yellow to Red
        r = 255
        g = int(255 * (2 - normalized * 2))
    
    b = 0
    
    return f"#{r:02x}{g:02x}{b:02x}"


def batch_process(items: List[Any], batch_size: int = 100):
    """
    Generator to process items in batches
    
    Usage:
        for batch in batch_process(items, 50):
            process(batch)
    """
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]


def retry_on_failure(func, max_retries: int = 3, delay: float = 1.0):
    """
    Retry function on failure
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
    """
    import time
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
            time.sleep(delay)


def sanitize_filename(filename: str) -> str:
    """Remove invalid characters from filename"""
    import re
    return re.sub(r'[^\w\s-]', '', filename).strip().replace(' ', '_')


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def generate_unique_id(prefix: str = "") -> str:
    """Generate unique identifier"""
    import uuid
    unique_id = str(uuid.uuid4())
    return f"{prefix}{unique_id}" if prefix else unique_id


def merge_dicts(*dicts: Dict) -> Dict:
    """Merge multiple dictionaries"""
    result = {}
    for d in dicts:
        result.update(d)
    return result


def filter_none_values(data: Dict) -> Dict:
    """Remove None values from dictionary"""
    return {k: v for k, v in data.items() if v is not None}


def flatten_dict(data: Dict, parent_key: str = '', sep: str = '_') -> Dict:
    """Flatten nested dictionary"""
    items = []
    for k, v in data.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def get_nested_value(data: Dict, path: str, default: Any = None) -> Any:
    """
    Get nested dictionary value using dot notation
    
    Example:
        get_nested_value({'a': {'b': {'c': 1}}}, 'a.b.c') -> 1
    """
    keys = path.split('.')
    value = data
    
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
            if value is None:
                return default
        else:
            return default
    
    return value


# ============================================================================
# VALIDATION HELPERS
# ============================================================================

def validate_email(email: str) -> bool:
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate phone number (Kenya format)"""
    import re
    # Kenya phone: +254... or 07... or 01...
    pattern = r'^(\+254|0)[17]\d{8}
    return re.match(pattern, phone) is not None


def validate_url(url: str) -> bool:
    """Validate URL format"""
    import re
    pattern = r'^https?://[^\s/$.?#].[^\s]*
    return re.match(pattern, url) is not None


# ============================================================================
# TIME HELPERS
# ============================================================================

def time_ago(dt: datetime) -> str:
    """Convert datetime to 'time ago' string"""
    now = datetime.now()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    elif seconds < 3600:
        return f"{int(seconds / 60)} minutes ago"
    elif seconds < 86400:
        return f"{int(seconds / 3600)} hours ago"
    elif seconds < 604800:
        return f"{int(seconds / 86400)} days ago"
    elif seconds < 2592000:
        return f"{int(seconds / 604800)} weeks ago"
    elif seconds < 31536000:
        return f"{int(seconds / 2592000)} months ago"
    else:
        return f"{int(seconds / 31536000)} years ago"


def get_business_days(start_date: date, end_date: date) -> int:
    """Calculate number of business days between dates"""
    days = 0
    current = start_date
    
    while current <= end_date:
        if current.weekday() < 5:  # Monday = 0, Friday = 4
            days += 1
        current += timedelta(days=1)
    
    return days


def add_business_days(start_date: date, days: int) -> date:
    """Add business days to a date"""
    current = start_date
    added = 0
    
    while added < days:
        current += timedelta(days=1)
        if current.weekday() < 5:
            added += 1
    
    return current