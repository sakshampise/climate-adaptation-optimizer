"""External API integrations layer."""

from src.integrations.base import BaseClient, IntegrationError
from src.integrations.open_meteo import OpenMeteoClient

__all__ = [
    "BaseClient",
    "IntegrationError",
    "OpenMeteoClient",
]
