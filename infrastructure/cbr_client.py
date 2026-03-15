import requests
from xml.etree import ElementTree as ET

from utils.date_utils import convert_date_to_cbr
from infrastructure.xml_parser import parse_cbr_xml


def get_currency_rates(date_str: str | None = None) -> dict:
    url = "https://www.cbr.ru/scripts/XML_daily.asp"

    if date_str:
        cbr_date = convert_date_to_cbr(date_str)
        response = requests.get(url, params={"date_req": cbr_date}, timeout=10)
    else:
        response = requests.get(url, timeout=10)

    response.raise_for_status()

    root = ET.fromstring(response.text)
    return parse_cbr_xml(root)