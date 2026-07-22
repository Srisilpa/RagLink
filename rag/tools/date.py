from datetime import datetime


def get_date():

    return datetime.now().strftime(
        "%d %B %Y"
    )


def get_time():

    return datetime.now().strftime(
        "%I:%M %p"
    )