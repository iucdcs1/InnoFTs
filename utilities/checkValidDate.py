from datetime import datetime


def is_valid_date(input_date):
    try:
        datetime.strptime(input_date, '%d.%m.%Y')
        return True
    except ValueError:
        return False