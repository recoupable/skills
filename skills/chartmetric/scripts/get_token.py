#!/usr/bin/env python3
"""
Get or refresh Chartmetric access token.
Token is cached in /tmp/chartmetric_token.json

Usage:
    python get_token.py

Environment:
    CHARTMETRIC_REFRESH_TOKEN - Your Chartmetric refresh token
"""

import os
import json
import time
import requests
from pathlib import Path

CACHE_FILE = Path("/tmp/chartmetric_token.json")
API_BASE = "https://api.chartmetric.com/api"


def get_token() -> str:
    """Get a valid access token, refreshing if needed."""
    
    # Check cache
    if CACHE_FILE.exists():
        try:
            cached = json.loads(CACHE_FILE.read_text())
            if cached["expires_at"] > time.time() + 60:
                return cached["access_token"]
        except (json.JSONDecodeError, KeyError):
            pass  # Cache invalid, refresh
    
    # Refresh token
    refresh_token = os.environ.get("CHARTMETRIC_REFRESH_TOKEN")
    if not refresh_token:
        raise ValueError("CHARTMETRIC_REFRESH_TOKEN environment variable not set")
    
    response = requests.post(
        f"{API_BASE}/token",
        json={"refreshtoken": refresh_token}
    )
    response.raise_for_status()
    data = response.json()
    
    # Cache it
    cached = {
        "access_token": data["token"],
        "expires_at": time.time() + data.get("expires_in", 3600)
    }
    CACHE_FILE.write_text(json.dumps(cached))
    
    return cached["access_token"]


if __name__ == "__main__":
    token = get_token()
    print(token)
