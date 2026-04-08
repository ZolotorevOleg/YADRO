from unittest.mock import patch
import requests

from main import app


def test_info():
    client = app.test_client()

    response = client.get("/info")
    data = response.get_json()

    assert response.status_code == 200
    assert "version" in data
    assert "service" in data
    assert "author" in data
    assert data["service"] == "currency"
    assert data["author"] == "o.zolotorev1"


@patch("main.get_rates")
def test_currency_without_params(mock_get_rates):
    mock_get_rates.return_value = {
        "USD": 90.5,
        "EUR": 98.1
    }

    client = app.test_client()
    response = client.get("/info/currency")
    data = response.get_json()

    assert response.status_code == 200
    assert data["service"] == "currency"
    assert "data" in data
    assert data["data"]["USD"] == 90.5
    mock_get_rates.assert_called_once_with(None)


@patch("main.get_rates")
def test_currency_by_code(mock_get_rates):
    mock_get_rates.return_value = {
        "USD": 90.5,
        "EUR": 98.1
    }

    client = app.test_client()
    response = client.get("/info/currency?currency=usd")
    data = response.get_json()

    assert response.status_code == 200
    assert data["service"] == "currency"
    assert data["data"] == {"USD": 90.5}


@patch("main.validate_date")
def test_currency_invalid_date(mock_validate_date):
    mock_validate_date.return_value = False

    client = app.test_client()
    response = client.get("/info/currency?date=2026/01/01")
    data = response.get_json()

    assert response.status_code == 400
    assert data["error"] == "Invalid date format. Use YYYY-MM-DD"


@patch("main.validate_date_not_future")
@patch("main.validate_date")
def test_currency_future_date(mock_validate_date,
                              mock_validate_date_not_future):
    mock_validate_date.return_value = True
    mock_validate_date_not_future.return_value = False

    client = app.test_client()
    response = client.get("/info/currency?date=2099-01-01")
    data = response.get_json()

    assert response.status_code == 400
    assert data["error"] == "Future dates are not allowed"


@patch("main.get_rates")
def test_currency_not_found(mock_get_rates):
    mock_get_rates.return_value = {
        "USD": 90.5,
        "EUR": 98.1
    }

    client = app.test_client()
    response = client.get("/info/currency?currency=GBP")
    data = response.get_json()

    assert response.status_code == 404
    assert data["error"] == "Currency 'GBP' not found"


@patch("main.get_rates")
def test_currency_request_exception(mock_get_rates):
    mock_get_rates.side_effect = requests.RequestException()

    client = app.test_client()
    response = client.get("/info/currency")
    data = response.get_json()

    assert response.status_code == 500
    assert data["error"] == "Failed to fetch currency rates"


@patch("main.get_rates")
def test_currency_parse_exception(mock_get_rates):
    mock_get_rates.side_effect = Exception()

    client = app.test_client()
    response = client.get("/info/currency")
    data = response.get_json()

    assert response.status_code == 500
    assert data["error"] == "Failed to parse currency rates"
