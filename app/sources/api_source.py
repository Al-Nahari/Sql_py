"""
Source #2: REST API containing academic data
(student_id, gpa, attendance, status).

Talks to a local mock API server over real HTTP using `requests`,
so the full HTTP request/response/error-handling flow described in
the assignment (Connection Error, Timeout, HTTP Error, Invalid JSON,
Empty Response) is genuinely exercised, not simulated.
"""

from __future__ import annotations

import time

import pandas as pd
import requests

from app.mock_api.server import start_mock_api_server
from app.utils.logger import get_logger

logger = get_logger(__name__)


class APIExtractionError(Exception):
    """Raised when the API source cannot be extracted after all retries."""


def extract_api(
    host: str = "127.0.0.1",
    port: int = 8899,
    path: str = "/students",
    timeout: int = 5,
    retries: int = 3,
    retry_backoff_seconds: float = 0.5,
) -> pd.DataFrame:
    """Fetch academic records from the REST API.

    HTTP Request -> Receive JSON -> Parse JSON -> Convert to DataFrame,
    with retries and explicit handling for every failure mode called
    out in the assignment.
    """
    logger.info("API extraction started")

    # Make sure something is listening. In a real project this line
    # would simply not exist because the API would already be running
    # somewhere; here it guarantees the demo works offline too.
    start_mock_api_server(host=host, port=port)

    url = f"http://{host}:{port}{path}"
    last_error: Exception | None = None

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
        except requests.exceptions.ConnectionError as exc:
            last_error = exc
            logger.warning(
                "API connection error on attempt %s/%s: %s", attempt, retries, exc
            )
        except requests.exceptions.Timeout as exc:
            last_error = exc
            logger.warning("API timeout on attempt %s/%s: %s", attempt, retries, exc)
        except requests.exceptions.HTTPError as exc:
            last_error = exc
            logger.warning(
                "API returned HTTP error on attempt %s/%s: %s", attempt, retries, exc
            )
        else:
            if not response.content:
                last_error = APIExtractionError("Empty response body from API")
                logger.warning(
                    "API returned an empty response on attempt %s/%s", attempt, retries
                )
            else:
                try:
                    payload = response.json()
                except ValueError as exc:
                    last_error = exc
                    logger.warning(
                        "API returned invalid JSON on attempt %s/%s: %s",
                        attempt,
                        retries,
                        exc,
                    )
                else:
                    df = pd.DataFrame(payload)
                    logger.info("API records: %s", len(df))
                    return df

        if attempt < retries:
            time.sleep(retry_backoff_seconds)

    logger.error("API extraction failed after %s attempts: %s", retries, last_error)
    raise APIExtractionError(
        f"Could not extract data from API after {retries} attempts: {last_error}"
    )
