import os
from utils.validators import validate_date, validate_date_not_future
from services.currency_service import get_rates

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
        rates = get_rates(date_str)
    except requests.RequestException:
        return jsonify({"error": "Failed to fetch currency rates"}), 500
    except Exception:
        return jsonify({"error": "Failed to parse currency rates"}), 500

    if currency_code:
        currency_code = currency_code.upper()

        if currency_code not in rates:
            return jsonify({"error": f"Currency '{currency_code}' "
                                     "not found"}), 404

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
