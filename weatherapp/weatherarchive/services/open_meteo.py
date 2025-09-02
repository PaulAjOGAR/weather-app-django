import time
from datetime import date
from typing import Dict, Optional, Tuple

import requests

try:
    # Optional dependencies; if not installed, fallback to plain requests
    import requests_cache  # type: ignore
    from retry_requests import retry  # type: ignore
except Exception:  # pragma: no cover - optional
    requests_cache = None
    retry = None


def _build_session() -> requests.Session:
    """Build a requests session with optional caching and retries."""
    sess = requests.Session()
    # Install caching if available
    if requests_cache is not None:
        # Cache for 10 minutes to reduce repeated lookups during exploration
        requests_cache.install_cache(
            cache_name="open_meteo_cache",
            backend="sqlite",
            expire_after=600,
        )
    # Add basic retry if available
    if retry is not None:
        sess = retry(sess, retries=3, backoff_factor=0.5)
    return sess


_session = _build_session()


def geocode(name: str) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    """Return (lat, lon, display_name) from Open-Meteo geocoding API or (None, None, None)."""
    try:
        r = _session.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": name, "count": 1},
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
        if not data.get("results"):
            return None, None, None
        top = data["results"][0]
        display = f"{top.get('name')}, {top.get('country_code', '')}".strip(", ")
        return top["latitude"], top["longitude"], display
    except Exception:
        return None, None, None


def fetch_daily(lat: float, lon: float, start: date, end: date) -> Dict:
    """Fetch daily history from Open-Meteo Archive API."""
    daily_params = ",".join([
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_sum",
        "windspeed_10m_max",
    ])
    r = _session.get(
        "https://archive-api.open-meteo.com/v1/archive",
        params={
            "latitude": lat,
            "longitude": lon,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "daily": daily_params,
            "timezone": "auto",
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def fetch_hourly(lat: float, lon: float, start: date, end: date) -> Dict:
    """Fetch hourly history from Open-Meteo Archive API (basic common vars)."""
    hourly_params = ",".join([
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "windspeed_10m",
    ])
    r = _session.get(
        "https://archive-api.open-meteo.com/v1/archive",
        params={
            "latitude": lat,
            "longitude": lon,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "hourly": hourly_params,
            "timezone": "auto",
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()
