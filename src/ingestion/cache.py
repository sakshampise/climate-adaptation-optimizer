"""Disk and memory caching module for API responses and climate summaries.

Ensures minimal external API consumption, respects rate limits, and enables
graceful degradation when external networks or services are unavailable.
"""

from datetime import datetime, timezone
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


DEFAULT_CACHE_DIR = Path("data/cache/climate")


class ClimateCache:
    """Thread-safe and process-safe JSON-file backed cache with configurable TTL."""

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = Path(cache_dir) if cache_dir else DEFAULT_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, key: str) -> Path:
        safe_key = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in key)
        return self.cache_dir / f"{safe_key}.json"

    def get(self, key: str) -> Optional[Tuple[Dict[str, Any], float, str]]:
        """Retrieves cached data if it exists and has not expired.

        Returns:
            Tuple of (data_dict, age_seconds, retrieval_timestamp_iso) or None.
        """
        path = self._get_path(key)
        if not path.exists():
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                record = json.load(f)

            cached_at = float(record.get("_cached_at", 0))
            ttl = float(record.get("_ttl", 0))
            now = time.time()
            age = max(0.0, now - cached_at)

            if age > ttl:
                return None  # Expired

            retrieval_ts = str(record.get("_retrieval_timestamp") or datetime.fromtimestamp(cached_at, tz=timezone.utc).isoformat())
            return record.get("data"), age, retrieval_ts
        except Exception:
            return None

    def get_stale(self, key: str) -> Optional[Tuple[Dict[str, Any], float, str]]:
        """Retrieves cached data even if expired (for offline/emergency fallback).

        Returns:
            Tuple of (data_dict, age_seconds, retrieval_timestamp_iso) or None.
        """
        path = self._get_path(key)
        if not path.exists():
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                record = json.load(f)

            cached_at = float(record.get("_cached_at", 0))
            age = max(0.0, time.time() - cached_at)
            retrieval_ts = str(record.get("_retrieval_timestamp") or datetime.fromtimestamp(cached_at, tz=timezone.utc).isoformat())
            return record.get("data"), age, retrieval_ts
        except Exception:
            return None

    def set(
        self,
        key: str,
        data: Dict[str, Any],
        ttl_seconds: int = 3600,
        retrieval_timestamp: Optional[str] = None,
    ) -> None:
        """Stores data with a specified TTL using concurrency-safe atomic file replacement."""
        path = self._get_path(key)
        now_ts = time.time()
        record = {
            "_cached_at": now_ts,
            "_retrieval_timestamp": retrieval_timestamp or datetime.now(timezone.utc).isoformat(),
            "_ttl": ttl_seconds,
            "data": data,
        }

        # Concurrency safety: Write to a unique temporary file in the same directory, then atomic replace
        temp_file_path = None
        try:
            temp_fd, temp_file_path = tempfile.mkstemp(
                prefix=f"{path.stem}_",
                suffix=".tmp",
                dir=str(self.cache_dir),
            )
            with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
                json.dump(record, f, indent=2)
            os.replace(temp_file_path, path)
        except Exception:
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except OSError:
                    pass

    def clear(self) -> None:
        """Removes all cached JSON entries."""
        try:
            for item in self.cache_dir.glob("*.json"):
                item.unlink(missing_ok=True)
            for tmp in self.cache_dir.glob("*.tmp"):
                tmp.unlink(missing_ok=True)
        except Exception:
            pass
