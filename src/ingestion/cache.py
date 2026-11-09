"""Disk and memory caching module for API responses and climate summaries.

Ensures minimal external API consumption, respects rate limits, and enables
graceful degradation when external networks or services are unavailable.
"""

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


DEFAULT_CACHE_DIR = Path("data/cache/climate")


class ClimateCache:
    """JSON-file backed cache with configurable Time-To-Live (TTL)."""

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = Path(cache_dir) if cache_dir else DEFAULT_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, key: str) -> Path:
        safe_key = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in key)
        return self.cache_dir / f"{safe_key}.json"

    def get(self, key: str) -> Optional[Tuple[Dict[str, Any], float]]:
        """Retrieves cached data if it exists and has not expired.

        Returns:
            Tuple of (data_dict, freshness_seconds) or None if absent or expired.
        """
        path = self._get_path(key)
        if not path.exists():
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                record = json.load(f)

            cached_at = record.get("_cached_at", 0)
            ttl = record.get("_ttl", 0)
            now = time.time()
            age = now - cached_at

            if age > ttl:
                return None  # Expired

            return record.get("data"), age
        except Exception:
            return None

    def get_stale(self, key: str) -> Optional[Tuple[Dict[str, Any], float]]:
        """Retrieves cached data even if expired (for offline/emergency fallback).

        Returns:
            Tuple of (data_dict, age_seconds) or None if file doesn't exist or is unparseable.
        """
        path = self._get_path(key)
        if not path.exists():
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                record = json.load(f)

            cached_at = record.get("_cached_at", 0)
            age = time.time() - cached_at
            return record.get("data"), age
        except Exception:
            return None

    def set(self, key: str, data: Dict[str, Any], ttl_seconds: int = 3600) -> None:
        """Stores data with a specified TTL."""
        path = self._get_path(key)
        record = {
            "_cached_at": time.time(),
            "_ttl": ttl_seconds,
            "data": data,
        }
        try:
            temp_path = path.with_suffix(".tmp")
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(record, f, indent=2)
            temp_path.replace(path)
        except Exception:
            # If filesystem write fails, fail silently without crashing app
            pass

    def clear(self) -> None:
        """Removes all cached JSON entries."""
        try:
            for item in self.cache_dir.glob("*.json"):
                item.unlink(missing_ok=True)
        except Exception:
            pass
