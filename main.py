import os
from datetime import datetime
from xml.etree import ElementTree as ET

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv()

app = Flask(__name__)
app.json.sort_keys = False

VERSION = os.getenv("VERSION", "1.0.0")
AUTHOR = os.getenv("AUTHOR", "o.zolotorev1")
PORT = int(os.getenv("PORT", "8000"))

SERVICE_NAME = "currency"


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


def convert_date_to_cbr(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%d/%m/%Y")


def parse_cbr_xml(xml_text: str) -> dict:
    root = ET.fromstring(xml_text)
    result = {}

    for valute in root.findall("Valute"):
        char_code = valute.findtext("CharCode")
        value_text = valute.findtext("Value")
        nominal_text = valute.findtext("Nominal")

        if not char_code or not value_text or not nominal_text:
            continue

        value = float(value_text.replace(",", "."))
        nominal = int(nominal_text)

        result[char_code] = round(value / nominal, 4)

    return result


def get_currency_rates(date_str: str | None = None) -> tuple[dict, str | None]:
    url = "https://www.cbr.ru/scripts/XML_daily.asp"

    if date_str:
        cbr_date = convert_date_to_cbr(date_str)
        response = requests.get(url, params={"date_req": cbr_date}, timeout=10)
    else:
        response = requests.get(url, timeout=10)

    response.raise_for_status()

    root = ET.fromstring(response.text)
    actual_date = root.attrib.get("Date")

    return parse_cbr_xml(response.text), actual_date


@app.route("/info", methods=["GET"], strict_slashes=False)
def info():
    return jsonify({
        "version": VERSION,
        "service": SERVICE_NAME,
        "author": AUTHOR
    })


@app.route("/info/currency", methods=["GET"], strict_slashes=False)
def currency():
    currency_code = request.args.get("currency")
    date_str = request.args.get("date")

    if date_str and not validate_date(date_str):
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    if date_str and not validate_date_not_future(date_str):
        return jsonify({"error": "Future dates are not allowed"}), 400

    try:
        rates, actual_date = get_currency_rates(date_str)
    except requests.RequestException:
        return jsonify({"error": "Failed to fetch currency rates"}), 500
    except Exception:
        return jsonify({"error": "Failed to parse currency rates"}), 500

    if currency_code:
        currency_code = currency_code.upper()

        if currency_code not in rates:
            return jsonify({"error": f"Currency '{currency_code}' not found"}), 404

        return jsonify({
            "service": SERVICE_NAME,
            "data": {
                currency_code: rates[currency_code]
            }
        })

    return jsonify({
        "service": SERVICE_NAME,
        "data": rates
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)