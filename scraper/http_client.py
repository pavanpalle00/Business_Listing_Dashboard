"""A small, polite HTTP client shared by every scraper.

Features:
* one ``requests.Session`` (re-uses TCP connections)
* an identifying User-Agent header
* a fixed delay between requests so we never hammer a server
* automatic retries with exponential back-off on 429 / 5xx / timeouts
"""
import logging
import time

import requests

from . import config

log = logging.getLogger(__name__)

RETRY_STATUS = {429, 500, 502, 503, 504}


class PoliteClient:
    def __init__(self, delay: float = config.REQUEST_DELAY):
        self.delay = delay
        self._last_request = 0.0
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": config.USER_AGENT})

    def _wait_turn(self) -> None:
        """Sleep just long enough to keep ``delay`` seconds between calls."""
        elapsed = time.monotonic() - self._last_request
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self._last_request = time.monotonic()

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        kwargs.setdefault("timeout", config.REQUEST_TIMEOUT)
        last_error: Exception | None = None

        for attempt in range(1, config.MAX_RETRIES + 1):
            self._wait_turn()
            try:
                response = self.session.request(method, url, **kwargs)
                if response.status_code not in RETRY_STATUS:
                    response.raise_for_status()
                    return response
                last_error = requests.HTTPError(f"HTTP {response.status_code}")
            except (requests.ConnectionError, requests.Timeout) as exc:
                last_error = exc

            backoff = 2 ** attempt
            log.warning("%s %s failed (%s), retry %d/%d in %ds",
                        method, url, last_error, attempt, config.MAX_RETRIES, backoff)
            time.sleep(backoff)

        raise RuntimeError(f"{method} {url} failed after {config.MAX_RETRIES} attempts: {last_error}")

    def get(self, url: str, **kwargs) -> requests.Response:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> requests.Response:
        return self.request("POST", url, **kwargs)
