"""Base HTTP client with retry handling, exponential backoff, and timeouts."""

import logging
import time
from typing import Any, Dict, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class IntegrationError(Exception):
    """Raised when an external API integration fails after retries."""
    pass


class BaseClient:
    """Base HTTP client providing resilient connection pooling, retries, and timeouts."""

    DEFAULT_TIMEOUT_SECONDS: float = 8.0
    DEFAULT_MAX_RETRIES: int = 3
    DEFAULT_BACKOFF_FACTOR: float = 0.5
    DEFAULT_USER_AGENT: str = "PuneClimateOptimizer/1.0 (+https://github.com/sakshampise/climate-adaptation-optimizer)"

    def __init__(
        self,
        base_url: str,
        timeout_seconds: Optional[float] = None,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[float] = None,
        session: Optional[requests.Session] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds or self.DEFAULT_TIMEOUT_SECONDS
        self.max_retries = max_retries or self.DEFAULT_MAX_RETRIES
        self.backoff_factor = backoff_factor or self.DEFAULT_BACKOFF_FACTOR

        if session is not None:
            self.session = session
        else:
            self.session = requests.Session()
            retry_strategy = Retry(
                total=self.max_retries,
                backoff_factor=self.backoff_factor,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET", "HEAD"],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount("https://", adapter)
            self.session.mount("http://", adapter)

        self.session.headers.update({"User-Agent": self.DEFAULT_USER_AGENT})

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Performs a GET request with automatic retry and JSON deserialization.

        Args:
            endpoint: Relative or absolute endpoint path.
            params: Optional query parameters.

        Returns:
            Parsed JSON dictionary from API response.

        Raises:
            IntegrationError: If request fails, times out, or returns non-200.
        """
        url = endpoint if endpoint.startswith("http") else f"{self.base_url}/{endpoint.lstrip('/')}"

        start_time = time.time()
        try:
            response = self.session.get(url, params=params, timeout=self.timeout_seconds)
            elapsed_ms = (time.time() - start_time) * 1000

            if response.status_code != 200:
                raise IntegrationError(
                    f"API request failed with status {response.status_code}: {response.text[:200]}"
                )

            data = response.json()
            logger.debug("Successfully called %s in %.1f ms", url, elapsed_ms)
            return data

        except requests.exceptions.RequestException as exc:
            elapsed_ms = (time.time() - start_time) * 1000
            raise IntegrationError(
                f"External API error calling {url} after {elapsed_ms:.1f}ms: {exc}"
            ) from exc
