import time
import requests

API_BASE_URL = "https://api.frankfurter.dev/v2"
TIMEOUT_SECONDS = 3
MAX_RETRIES = 1


def get_json(path, params=None):
    """
    Wrapper HTTP simple :
    - timeout 3 secondes
    - 1 retry max
    - mesure de latence
    - gestion 429 / 5xx / timeout
    """
    url = f"{API_BASE_URL}{path}"
    headers = {
        "Accept": "application/json",
        "User-Agent": "atelier-api-tests/1.0"
    }

    last_error = None

    for attempt in range(MAX_RETRIES + 1):
        start = time.perf_counter()

        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=TIMEOUT_SECONDS
            )

            latency_ms = round((time.perf_counter() - start) * 1000, 2)

            if response.status_code == 429 and attempt < MAX_RETRIES:
                time.sleep(1)
                continue

            if 500 <= response.status_code <= 599 and attempt < MAX_RETRIES:
                time.sleep(1)
                continue

            try:
                json_body = response.json()
            except ValueError:
                json_body = None

            return {
                "url": response.url,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "json": json_body,
                "latency_ms": latency_ms,
                "error": None
            }

        except requests.Timeout:
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            last_error = f"Timeout après {TIMEOUT_SECONDS}s"
            if attempt < MAX_RETRIES:
                time.sleep(1)
                continue

            return {
                "url": url,
                "status_code": 0,
                "headers": {},
                "json": None,
                "latency_ms": latency_ms,
                "error": last_error
            }

        except requests.RequestException as exc:
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            last_error = str(exc)
            if attempt < MAX_RETRIES:
                time.sleep(1)
                continue

            return {
                "url": url,
                "status_code": 0,
                "headers": {},
                "json": None,
                "latency_ms": latency_ms,
                "error": last_error
            }