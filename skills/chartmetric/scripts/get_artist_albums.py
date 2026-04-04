#!/usr/bin/env python3
"""
Get artist's albums.

Usage:
    python get_artist_albums.py <chartmetric_id>
    python get_artist_albums.py 3380

Environment:
    CHARTMETRIC_REFRESH_TOKEN - Your Chartmetric refresh token
"""

import sys
import json
import requests
from get_token import get_token

API_BASE = "https://api.chartmetric.com/api"


def get_artist_albums(cm_id: str) -> dict:
    """Fetch artist's albums from Chartmetric."""
    token = get_token()
    
    response = requests.get(
        f"{API_BASE}/artist/{cm_id}/albums",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 402:
        return {"error": "Payment Required", "message": "Check your Chartmetric subscription."}
    
    if response.status_code == 404:
        return {"error": "Artist not found", "chartmetric_id": cm_id}
    
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_artist_albums.py <chartmetric_id>")
        sys.exit(1)
    
    result = get_artist_albums(sys.argv[1])
    
    if "error" in result:
        print(f"Error: {result.get('error')}")
        if "message" in result:
            print(result.get('message'))
        sys.exit(1)
    
    albums = result.get("obj", [])
    print(f"Found {len(albums)} albums:\n")
    for album in albums[:20]:  # Limit to first 20
        print(f"- {album.get('name')}")
        print(f"  Chartmetric ID: {album.get('id')}")
        print(f"  Release: {album.get('release_date', 'N/A')}")
        print()
