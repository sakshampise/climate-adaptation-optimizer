"""Open-Meteo API integration client for live weather forecasts and historical climate archives."""

from typing import Any, Dict, Optional
import requests
from src.integrations.base import BaseClient, IntegrationError


class OpenMeteoClient:
    """Client for Open-Meteo Weather Forecast and Historical Archive APIs."""

    FORECAST_URL = "https://api.open-meteo.com/v1"
    ARCHIVE_URL = "https://archive-api.open-meteo.com/v1"

    def __init__(
        self,
        timeout_seconds: float = 6.0,
        max_retries: int = 3,
        session: Optional[requests.Session] = None,
    ):
        self.forecast_client = BaseClient(
            base_url=self.FORECAST_URL,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            session=session,
        )
        self.archive_client = BaseClient(
            base_url=self.ARCHIVE_URL,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            session=session,
        )

    def fetch_current_and_forecast(
        self,
        latitude: float,
        longitude: float,
        timezone: str = "Asia/Kolkata",
    ) -> Dict[str, Any]:
        """Fetches current weather and 7-day daily forecast for specified coordinates.

        Args:
            latitude: Geographic latitude in decimal degrees.
            longitude: Geographic longitude in decimal degrees.
            timezone: Target timezone for daily day boundaries.

        Returns:
            Raw API response dict from Open-Meteo Forecast endpoint.

        Raises:
            IntegrationError: If network fails or non-200 received after retries.
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_hours,precipitation_probability_max",
            "timezone": timezone,
        }
        return self.forecast_client.get("forecast", params=params)

    def fetch_historical_archive(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
        timezone: str = "Asia/Kolkata",
    ) -> Dict[str, Any]:
        """Fetches historical daily weather records from Open-Meteo ERA5 archive.

        Args:
            latitude: Geographic latitude in decimal degrees.
            longitude: Geographic longitude in decimal degrees.
            start_date: Start date formatted as YYYY-MM-DD.
            end_date: End date formatted as YYYY-MM-DD.
            timezone: Target timezone for day aggregation.

        Returns:
            Raw API response dict from Open-Meteo Archive endpoint.

        Raises:
            IntegrationError: If network fails or non-200 received after retries.
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_hours",
            "timezone": timezone,
        }
        return self.archive_client.get("archive", params=params)
