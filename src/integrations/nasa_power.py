"""NASA POWER API integration client for multi-decadal solar and meteorological climatology."""

from typing import Any, Dict, List, Optional
import requests
from src.integrations.base import BaseClient, IntegrationError


class NasaPowerClient:
    """Client for NASA POWER (Prediction of Worldwide Energy Resources) API."""

    BASE_URL = "https://power.larc.nasa.gov/api"
    DEFAULT_PARAMETERS = ["ALLSKY_SFC_SW_DWN", "TS", "PRECTOTCORR"]

    def __init__(
        self,
        timeout_seconds: float = 12.0,
        max_retries: int = 2,
        session: Optional[requests.Session] = None,
    ):
        self.client = BaseClient(
            base_url=self.BASE_URL,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            session=session,
        )

    def fetch_climatology(
        self,
        latitude: float,
        longitude: float,
        parameters: Optional[List[str]] = None,
        community: str = "RE",
    ) -> Dict[str, Any]:
        """Fetches multi-decadal climatology normals for specified coordinates.

        Args:
            latitude: Geographic latitude in decimal degrees.
            longitude: Geographic longitude in decimal degrees.
            parameters: List of NASA POWER parameter codes. Defaults to
                ['ALLSKY_SFC_SW_DWN', 'TS', 'PRECTOTCORR'].
            community: Application community code ('RE', 'SB', or 'AG'). Defaults to 'RE'.

        Returns:
            Raw API response dictionary from NASA POWER Climatology endpoint.

        Raises:
            IntegrationError: If network fails or non-200 status code received.
        """
        target_params = parameters if parameters is not None else self.DEFAULT_PARAMETERS
        query_params = {
            "parameters": ",".join(target_params),
            "community": community,
            "longitude": longitude,
            "latitude": latitude,
            "format": "JSON",
        }
        return self.client.get("temporal/climatology/point", params=query_params)
