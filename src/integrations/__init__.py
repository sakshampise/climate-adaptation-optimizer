"""External API integrations layer."""

from src.integrations.base import BaseClient, IntegrationError
from src.integrations.open_meteo import OpenMeteoClient
from src.integrations.nasa_power import NasaPowerClient

__all__ = [
    "BaseClient",
    "IntegrationError",
    "OpenMeteoClient",
    "NasaPowerClient",
]
