#!/usr/bin/env python3
"""
Get playlist metadata.

Usage:
    python get_playlist.py <platform> <playlist_id>
    python get_playlist.py spotify 37i9dQZF1DXcBWIGoYBM5M
    python get_playlist.py apple pl.f4d106fed2bd41149aaacabb233eb5eb

Environment:
    CHARTMETRIC_REFRESH_TOKEN - Your Chartmetric refresh token
"""

import sys
import json
import requests
from get_token import get_token

API_BASE = "https://api.chartmetric.com/api"


def get_playlist(platform: str, playlist_id: str) -> dict:
    """Fetch playlist metadata from Chartmetric."""
    token = get_token()
    
    response = requests.get(
        f"{API_BASE}/playlist/{platform}/{playlist_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    
    if response.status_code == 402:
        return {"error": "Payment Required", "message": "Check your Chartmetric subscription."}
    
    if response.status_code == 404:
        return {"error": "Playlist not found", "platform": platform, "playlist_id": playlist_id}
    
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python get_playlist.py <platform> <playlist_id>")
        print("Platforms: spotify, apple, deezer, amazon")
        sys.exit(1)
    
    result = get_playlist(sys.argv[1], sys.argv[2])
    print(json.dumps(result, indent=2))
