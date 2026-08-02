from datetime import datetime


def get_date():
    """
    Returns today's date.
    """
    return datetime.now().strftime("%Y-%m-%d")