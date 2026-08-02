from datetime import datetime


def get_time():
    """
    Returns current system time.
    """
    return datetime.now().strftime("%H:%M:%S")