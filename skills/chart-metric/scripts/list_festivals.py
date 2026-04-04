#!/usr/bin/env python3
"""
List music festivals.

Usage:
    python list_festivals.py

Environment:
    CHARTMETRIC_REFRESH_TOKEN - Your Chartmetric refresh token
"""

import json
import requests
from get_token import get_token

API_BASE = "https://api.chartmetric.com/api"


def list_festivals() -> dict:
    """Fetch festival list from Chartmetric."""
    token = get_token()
    
    response = requests.get(
        f"{API_BASE}/festival/list",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    result = list_festivals()
    festivals = result.get("obj", [])
    
    print(f"Found {len(festivals)} festivals:\n")
    for fest in festivals[:30]:
        print(f"- {fest.get('name')}")
        if fest.get('city'):
            print(f"  Location: {fest.get('city')}, {fest.get('country', '')}")
        print()
