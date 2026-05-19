from tester.client import get_json


def result(name, passed, latency_ms=None, details=""):
    return {
        "name": name,
        "status": "PASS" if passed else "FAIL",
        "latency_ms": latency_ms,
        "details": details
    }


def test_latest_rates_status_200():
    response = get_json("/rates", params={"base": "EUR", "quotes": "USD,GBP"})
    passed = response["status_code"] == 200

    return result(
        "GET /rates retourne HTTP 200",
        passed,
        response["latency_ms"],
        f"Code reçu : {response['status_code']}"
    )


def test_latest_rates_content_type_json():
    response = get_json("/rates", params={"base": "EUR", "quotes": "USD,GBP"})
    content_type = response["headers"].get("Content-Type", "")
    passed = response["status_code"] == 200 and "application/json" in content_type

    return result(
        "Content-Type JSON",
        passed,
        response["latency_ms"],
        f"Content-Type reçu : {content_type}"
    )


def test_latest_rates_schema():
    response = get_json("/rates", params={"base": "EUR", "quotes": "USD,GBP"})
    data = response["json"]

    passed = True
    details = "Schéma valide"

    if response["status_code"] != 200:
        passed = False
        details = f"Code HTTP inattendu : {response['status_code']}"

    elif not isinstance(data, list) or len(data) < 2:
        passed = False
        details = "Le JSON attendu doit être une liste avec au moins 2 taux"

    else:
        for item in data:
            if not isinstance(item, dict):
                passed = False
                details = "Un élément de la liste n'est pas un objet JSON"
                break

            required_fields = ["date", "base", "quote", "rate"]
            for field in required_fields:
                if field not in item:
                    passed = False
                    details = f"Champ manquant : {field}"
                    break

            if not passed:
                break

            if not isinstance(item["date"], str):
                passed = False
                details = "Le champ date doit être une chaîne"
                break

            if item["base"] != "EUR":
                passed = False
                details = "Le champ base doit être EUR"
                break

            if item["quote"] not in ["USD", "GBP"]:
                passed = False
                details = "La devise de sortie doit être USD ou GBP"
                break

            if not isinstance(item["rate"], (int, float)) or item["rate"] <= 0:
                passed = False
                details = "Le taux doit être un nombre positif"
                break

    return result(
        "Schéma JSON de /rates",
        passed,
        response["latency_ms"],
        details
    )


def test_single_rate_endpoint():
    response = get_json("/rate/EUR/USD")
    data = response["json"]

    passed = (
        response["status_code"] == 200
        and isinstance(data, dict)
        and data.get("base") == "EUR"
        and data.get("quote") == "USD"
        and isinstance(data.get("rate"), (int, float))
        and data.get("rate") > 0
    )

    return result(
        "GET /rate/EUR/USD retourne un taux valide",
        passed,
        response["latency_ms"],
        f"Réponse : {data}"
    )


def test_currencies_contains_eur_and_usd():
    response = get_json("/currencies")
    data = response["json"]

    codes = []
    if isinstance(data, list):
        codes = [item.get("iso_code") for item in data if isinstance(item, dict)]

    passed = (
        response["status_code"] == 200
        and "EUR" in codes
        and "USD" in codes
    )

    return result(
        "GET /currencies contient EUR et USD",
        passed,
        response["latency_ms"],
        f"Devises trouvées : EUR={'EUR' in codes}, USD={'USD' in codes}"
    )


def test_historical_rate():
    response = get_json(
        "/rates",
        params={
            "date": "2024-01-15",
            "base": "EUR",
            "quotes": "USD"
        }
    )

    data = response["json"]

    passed = (
        response["status_code"] == 200
        and isinstance(data, list)
        and len(data) >= 1
        and data[0].get("date") == "2024-01-15"
        and data[0].get("base") == "EUR"
        and data[0].get("quote") == "USD"
        and isinstance(data[0].get("rate"), (int, float))
    )

    return result(
        "Taux historique au 2024-01-15",
        passed,
        response["latency_ms"],
        f"Réponse : {data}"
    )


def test_invalid_currency_error():
    response = get_json("/rate/EUR/XXX")
    data = response["json"]

    passed = (
        response["status_code"] in [404, 422]
        and isinstance(data, dict)
        and "message" in data
    )

    return result(
        "Devise invalide : erreur attendue",
        passed,
        response["latency_ms"],
        f"Code reçu : {response['status_code']}, réponse : {data}"
    )


TESTS = [
    test_latest_rates_status_200,
    test_latest_rates_content_type_json,
    test_latest_rates_schema,
    test_single_rate_endpoint,
    test_currencies_contains_eur_and_usd,
    test_historical_rate,
    test_invalid_currency_error,
]