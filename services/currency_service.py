from infrastructure.cbr_client import get_currency_rates


def get_rates(date_str: str | None = None) -> dict:
    return get_currency_rates(date_str)