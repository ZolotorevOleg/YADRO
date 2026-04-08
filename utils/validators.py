from datetime import datetime


def validate_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_date_not_future(date_str: str) -> bool:
    req_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    today = datetime.now().date()
    return req_date <= today
