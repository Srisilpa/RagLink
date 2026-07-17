from datetime import datetime


def current_date():

    return datetime.now().strftime(
        "%d-%m-%Y"
    )