#!/usr/bin/env python3
"""
List all Chartmetric genres.

Usage:
    python list_genres.py

Environment:
    CHARTMETRIC_REFRESH_TOKEN - Your Chartmetric refresh token
"""

import json
import requests
from get_token import get_token

API_BASE = "https://api.chartmetric.com/api"


def list_genres() -> dict:
    """Fetch all genres from Chartmetric."""
    token = get_token()
    
    response = requests.get(
        f"{API_BASE}/genres",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    result = list_genres()
    genres = result.get("obj", [])
    
    print(f"Found {len(genres)} genres:\n")
    for genre in genres[:50]:
        print(f"- {genre.get('name')} (ID: {genre.get('id')})")
    
    if len(genres) > 50:
        print(f"\n... and {len(genres) - 50} more")
